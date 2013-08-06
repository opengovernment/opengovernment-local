# encoding: utf-8

import lxml.html
import re

from billy.scrape.legislators import LegislatorScraper, Legislator

tel_regex = re.compile('(\d{3})\D*(\d{3})\D*(\d{4})')

def clean_string(string):
    return string.replace(u'\u2019', "'").replace(u'\u00A0', ' ').strip()

# @note Can add end_date to role
# @note Party affiliation is not given on the official website.
class SanJoseLegislatorScraper(LegislatorScraper):
    jurisdiction = 'ca-san-jose'

    def scrape(self, term, chambers):
        # The links on http://www.sanjoseca.gov/index.aspx?NID=1187 may go off-
        # site, so use http://www.sanjoseca.gov/index.aspx?NID=146
        council_url = 'http://www.sanjoseca.gov/index.aspx?NID=146'
        doc = lxml.html.fromstring(self.urlopen(council_url))
        doc.make_links_absolute(council_url)

        tds = doc.xpath('//div[@id="Section1"]//td')
        assert len(tds) <= 11, 'expected 11 unique mayor and councilmember URLs, found %d' % len(tds)

        lines = []
        for text in doc.xpath('//div[@id="Section1"]/text()'):
            text = clean_string(text)
            if re.match('^(?:\d+|San) ', text):
                lines.append(text)
        address = '\n'.join(lines)

        emails = []
        for text in doc.xpath('//div[@id="Section1"]/script/text()'):
            # PhantomJS would be sweet here.
            emails.append(''.join(re.search('([^"]+)"\+"(@)"\+"([^"]+)', text).groups()))

        for index, td in enumerate(tds):
            for text in td.xpath('.//text()'):
                match = tel_regex.search(text.strip())
                if match:
                    phone = '-'.join(match.groups())
                    break

            url       = td.xpath('.//a[//strong]/@href')[0]
            photo_url = td.xpath('.//img/@src')[0]

	    # Extract district, name, role
            text      = td.xpath('.//strong/text()')[0]

            if 'District' in text:
                district = re.search('District \d+', text).group(0)
                name     = re.sub(', District \d+$', '', text)
                role     = None
                if 'Vice Mayor' in text:
                    name = name.replace('Vice Mayor ', '')
                    role = 'Vice Mayor'
            elif 'Mayor' in text:
                district = 'Mayor'
                name     = text.replace('Mayor ', '')
                role     = 'Mayor'
            else:
                self.logger.warning('Skipped: ' + text)

	    # Extract fax and secondary phone from councilmember's page
            phone2    = None
            fax       = None
            councilmember_doc = lxml.html.fromstring(self.urlopen(url))
            councilmember_doc.make_links_absolute(url)

            # @todo xpath needs to be constrained further; it matches more elements than necessary
            for text in councilmember_doc.xpath('//div[//img[@alt="Contact Us"]]//text()'):  # '//div[@id="quickLinks774"]//text()'):
		if re.match('\s*Fax.*\d', text, re.I):
                    fax = '-'.join(tel_regex.search(text).groups())
		if re.match('\s*Phone.*\d', text, re.I) or re.match('\s*Ph..*\d', text, re.I) or re.match('\s*Tel..*\d', text, re.I):
                    councilmember_phone = '-'.join(tel_regex.search(text).groups())
                    phone2 = councilmember_phone if councilmember_phone != phone else None

	    # Assign councilmember information
            legislator = Legislator(term, 'upper', district, name, email=emails[index], url=url, photo_url=photo_url, party=None)
            legislator.add_office('capitol', 'Council Office', address=address, phone=phone, secondary_phone=phone2, fax=fax)

            if role:
                legislator.add_role(role, term)

            legislator.add_source(url)

            self.save_legislator(legislator)
