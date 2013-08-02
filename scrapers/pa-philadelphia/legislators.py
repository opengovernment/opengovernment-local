# encoding: utf-8

import lxml.html
import re

from billy.scrape.legislators import LegislatorScraper, Legislator, Person

tel_regex = re.compile('(\d{3})\D*(\d{3})\D*(\d{4})')

def clean_string(string):
    return string.replace(u'\u2019', "'").replace(u'\u00A0', ' ').strip()

# #note Can add office_hours, facebook_url, twitter_url to mayor.
# @note Can add personal_url, facebook_url, twitter_url, flickr_url, youtube_url to councilmembers.
# @note Party affiliation is not given on the official website.
class PhiladelphiaLegislatorScraper(LegislatorScraper):
    jurisdiction = 'pa-philadelphia'

    def scrape(self, term, chambers):
        # The mayor doesn't sit on council.
        url = 'http://www.phila.gov/'
        doc = lxml.html.fromstring(self.urlopen(url))
        doc.make_links_absolute(url)

        # The mayor's name doesn't appear on the mayor's page!
        name  = re.search('Mayor (.+)', doc.xpath('//title/text()')[0].strip()).group(1)
        mayor = Person(name)
        mayor.add_source(url)

        url = 'http://www.phila.gov/mayor/'
        doc = lxml.html.fromstring(self.urlopen(url))
        doc.make_links_absolute(url)

        lines   = map(clean_string, doc.xpath('//div[contains(text(),"Mailing Address")]/following-sibling::text()')[1:])
        address = '\n'.join(lines)
        phone   = '-'.join(tel_regex.search(doc.xpath('//strong[contains(text(),"Phone")]/following-sibling::text()[1]')[0]).groups())
        fax     = '-'.join(tel_regex.search(doc.xpath('//strong[contains(text(),"Fax")]/following-sibling::text()[1]')[0]).groups())
        email   = clean_string(doc.xpath('//strong[contains(text(),"Email")]/following-sibling::text()[1]')[0])

        mayor.update(dict(url=url, email=email))
        mayor.add_office('capitol', 'Office of the Mayor', address=address, phone=phone, fax=fax)
        mayor.add_role('Mayor', term)
        mayor.add_source(url)

        self.save_object(mayor)



        council_url = 'http://philadelphiacitycouncil.net/council-members/'
        doc = lxml.html.fromstring(self.urlopen(council_url))
        doc.make_links_absolute(council_url)

        urls = set(doc.xpath('//a[contains(@href, "/council-members/council")]/@href'))
        assert len(urls) <= 17, 'expected 17 unique councilmember URLs, found %d' % len(urls)

        for url in urls:
            doc = lxml.html.fromstring(self.urlopen(url))
            doc.make_links_absolute(url)

            optional  = dict() # fields not all legislators will have
            name      = []
            roles     = []
            lines     = []
            phone1    = None
            phone2    = None
            fax       = None
            district  = 'At-Large' # default
            photo_url = (
                doc.xpath('//img[contains(@title, "brian picture")]/@src') or  # Special case for BRIAN J. O’NEILL
                doc.xpath('//img[contains(@class, "size-full")]/@src') or
                doc.xpath('//img[contains(@class, "size-medium")]/@src') or
                doc.xpath('//img[contains(@class, "size-thumbnail")]/@src')
            )[0]

            # That's an en dash, not a hyphen.
            parts = re.split(u'[,–]', doc.xpath('//h3/text()')[0])
            for index, part in enumerate(filter(None, parts)):
                part = clean_string(part)
                if index == 0:
                    if 'Councilman' in part:
                        optional['gender'] = 'Male'
                    elif 'Councilwoman' in part:
                        optional['gender'] = 'Female'
                    elif 'Council President' in part:
                        roles.append('Council President')
                    part = re.sub('^Council(?:man|woman| President)\s+', '', part)
                    name.append(part)
                elif part in ('Jr.', 'Sr.'):
                    name.append(part)
                elif 'District' in part:
                    district = part
                else:
                    roles.append(part)
            name = ', '.join(name)

            contact_url = doc.xpath('//a[text()="Contact"]/@href')[0]
            doc = lxml.html.fromstring(self.urlopen(contact_url))
            doc.make_links_absolute(contact_url)

            # @todo email, second office, personal_url are sometimes in another paragraph.
            if len(doc.xpath('//div[@class="post-entry"]/p')) > 1:
                self.logger.warning('Skipped paragraphs:\n' + '\n'.join(lxml.html.tostring(html) for html in doc.xpath('//div[@class="post-entry"]/p[position()>1]')))

            parts = doc.xpath('//div[@class="post-entry"]/p[position()=1]//text()') or doc.xpath('//div[@class="post-entry"]//text()')
            parts = map(clean_string, parts)
            for part in filter(None, parts):
                if re.match(r'^City Hall.+Room', part):
                    lines.append('City Hall, Room %s' % re.search('Room (\d+)', part).group(1))
                elif re.match(r'^FAX:', part, re.I) or re.match(r'^F:', part, re.I):
                    fax = '-'.join(tel_regex.search(part).groups())
                elif tel_regex.search(part):
                    if phone1:
                        self.logger.warning('Already have phone numbers for one office: ' + part)
                    else:
                        phones = tel_regex.findall(part)
                        phone1 = '-'.join(phones[0])
                        if len(phones) == 2:
                            phone2 = '-'.join(phones[1])
                        else:
                            phone2 = phone1[:8] + re.search(r'(?: or |/)(\d{4})$', parts[2]).group(1)
                elif '@' in part:
                    optional['email'] = re.search('\S+@\S+', part).group()
                elif re.match(r'^(?:, )?Philadelphia, PA(?: 19107(?:-3290)?)?$', part):
                    pass
                else: # @todo second office is sometimes in the same paragraph.
                    self.logger.warning('Skipped: ' + part)

            # Some Councilmembers have no zip code or only a 5-digit zip code.
            # All that changes between them is a room number.
            lines.append('Philadelphia, PA 19107-3290')
            address = '\n'.join(lines)

            legislator = Legislator(term, 'upper', district, name, url=url, photo_url=photo_url, party=None)
            legislator.update(optional)
            legislator.add_office('capitol', 'Council Office', address=address, phone=phone1, secondary_phone=phone2, fax=fax)
            legislator.add_source(url)

            for role in roles:
                legislator.add_role(role, term)

            self.save_legislator(legislator)
