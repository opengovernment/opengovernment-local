# encoding: utf-8

import lxml.html
import re
import string

from billy.scrape.legislators import LegislatorScraper, Legislator, Person

tel_regex = re.compile('(\d{3})\D*(\d{3})\D*(\d{4})')

def clean_string(string):
    return string.replace(u'\u2019', "'").replace(u'\u00A0', ' ').strip()

def cleanup_address(s, assume_capitol_zipcode = True):

    # Special case for Curtis Jones Jr.
    if re.match(r'^, ', s):
	s = string.replace(s, ', ', '', 1)

    # Add missing zipcode and/or ZIP+4
    if not assume_capitol_zipcode:
	return s
    elif re.match(r'.*Philadelphia.*PA', s) and not re.match(r'.*19107', s):
	return string.replace(s, 'PA', 'PA 19107-3290')
    elif re.match(r'.*19107-', s):
	return s
    else:
	return string.replace(s, '19107', '19107-3290')

def parse_phones(part):
    phones = tel_regex.findall(part)
    phone1 = '-'.join(phones[0])
    if len(phones) == 2:
	phone2 = '-'.join(phones[1])
    elif re.match(r'.* or \d{4}', part) or re.match(r'.*/\d{4}', part):
	phone2 = phone1[:8] + re.search(r'(?: or |/)(\d{4})$', part).group(1)
    else:
	phone2 = None
    return phone1, phone2

def parse_full_name(string):
	first_name  = ''
	middle_name = ''
	last_name   = ''

	name_parts = string.split()

	if len(name_parts) == 2:
		first_name = name_parts[0]
		last_name  = name_parts[1]
	elif len(name_parts) == 3:
		first_name  = name_parts[0]
		middle_name = name_parts[1]
		last_name   = name_parts[2]
	return first_name, middle_name, last_name

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
        full_name  = re.search('Mayor (.+)', doc.xpath('//title/text()')[0].strip()).group(1)
        first_name, middle_name, last_name = parse_full_name(full_name)
        mayor = Person(full_name, first_name, last_name, middle_name)
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
            full_name = []
            first_name  = ''
            middle_name = ''
            last_name   = ''
            suffixes    = ''
            roles     = []
            lines     = []
            lines_office2 = []
            has_office2 = bool(False)
            reached_contact_form = bool(False)
            phone1    = None
            phone1_office2 = None
            phone2    = None
            phone2_office2 = None
            fax       = None
            fax_office2 = None
            office_name = None
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
                    full_name.append(part)
		    first_name, middle_name, last_name = parse_full_name(full_name[0])
                elif part in ('Jr.', 'Sr.'):
                    full_name.append(part)
		    suffixes = part
                elif 'District' in part:
                    district = part
                else:
                    roles.append(part)
            full_name = ', '.join(full_name)

            contact_url = doc.xpath('//a[text()="Contact"]/@href')[0]
            doc = lxml.html.fromstring(self.urlopen(contact_url))
            doc.make_links_absolute(contact_url)

            # @todo email, personal_url are sometimes in another paragraph.

            parts = doc.xpath('//div[@class="post-entry"]//text()')
            parts = map(clean_string, parts)
	    consuming_address_lines = bool(False)
            for part in filter(None, parts):
 
		# Special case for Curtis Jones Jr.
                if re.match(r'^Local Office:', part):
		    consuming_address_lines = True
                    has_office2 = True
		    office_name = 'Local Office'

                if re.match(r'City Hall Office', part) or re.match(r'^Hours', part) or re.match(r'.*facebook', part) or re.match(r'.*twitter', part) or reached_contact_form:
		    continue

                elif re.match(r'^Contact Council.*man', part) or re.match(r'^Contact CMAL', part):
		    reached_contact_form = True
                    continue

                elif re.match(r'^City Hall.+Room', part):
		    consuming_address_lines = True
                    lines.append(part)

                elif re.match(r'^FAX:', part, re.I) or re.match(r'^F:', part, re.I):
		    consuming_address_lines = False
                    if has_office2 and fax_office2 == None:
               		fax_office2 = '-'.join(tel_regex.search(part).groups())
                    elif fax == None:
               		fax = '-'.join(tel_regex.search(part).groups())

                elif tel_regex.search(part):
		    consuming_address_lines = False
                    if has_office2 and phone1_office2 == None and phone2_office2 == None:
			phone1_office2, phone2_office2 = parse_phones(part)
                    elif phone1 == None and phone2 == None:
			phone1, phone2 = parse_phones(part)

                elif '@' in part:
		    consuming_address_lines = False
                    optional['email'] = re.search('\S+@\S+', part).group()

                elif re.match(r'^Neighborhood Office.*', part):
		    consuming_address_lines = False
                    has_office2 = True

                elif re.match(r'.*Office.*', part) or re.match(r'.*Heroes Hall.*', part):

		    # Special case for Curtis Jones Jr.
		    if re.match(r'.*Local Office.*', part):
			continue

		    if len(lines_office2) > 0:
			consuming_address_lines = False
		    else:
			consuming_address_lines = True
			office_name =  string.strip(part, ':;,.')

                elif consuming_address_lines:
                    if has_office2:
                    	lines_office2.append(cleanup_address(part, False))
                    else:
			lines.append(cleanup_address(part))

                elif re.match(r'^(?:, )?Philadelphia, PA(?: 19107(?:-3290)?)?$', part):
                    pass

                else:
                    self.logger.warning('Skipped: ' + part)

            # Some Councilmembers have no zip code or only a 5-digit zip code.
            # All that changes between them is a room number.
            address = '\n'.join(lines)
            address_office2 = '\n'.join(lines_office2)

            legislator = Legislator(term, 'upper', district, full_name, first_name, last_name, middle_name, suffixes=suffixes, url=url, photo_url=photo_url, party=None)
            legislator.update(optional)

	    if re.search('.*\S.*', address):
      		legislator.add_office('capitol', 'City Hall Office', address=address, phone=phone1, secondary_phone=phone2, fax=fax)

	    if re.search('.*\S.*', address_office2):
      		legislator.add_office('district', office_name, address=address_office2, phone=phone1_office2, secondary_phone=phone2_office2, fax=fax_office2)

            legislator.add_source(url)

            for role in roles:
                legislator.add_role(role, term)

            self.save_legislator(legislator)
