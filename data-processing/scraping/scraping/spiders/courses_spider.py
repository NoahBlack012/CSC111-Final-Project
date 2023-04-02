import scrapy

class CoursesSpider(scrapy.Spider):
    name = "courses"

    def start_requests(self):
        base_url = "https://artsci.calendar.utoronto.ca/search-courses?page="
        urls = [
            base_url + str(i) for i in range(0, 168)
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for n, row in enumerate(response.css("div.views-row")):
            if n % 2 == 0:
                course_name = row.css("h3.js-views-accordion-group-header::text").extract()[0].strip()
                course_code = course_name[0:8]

                try:
                    hours = row.css("span.views-field.views-field-field-hours").css("span.field-content *::text").extract()[0]
                except (AttributeError, IndexError):
                    hours = None

                try:
                    description_text = row.css("div.views-field.views-field-body").css("div.field-content *::text").extract()
                    description = ''.join(description_text)
                except (AttributeError, IndexError):
                    description = ''

                try:
                    text = row.css("span.views-field.views-field-field-prerequisite").css("span.field-content *::text").extract()
                    prereqs = process_course_requirements(text, course_code)
                    prereq_text = ''.join(text)
                except (AttributeError, IndexError):
                    prereqs = ''
                    prereq_text = ''

                try:
                    text = row.css("span.views-field.views-field-field-corequisite").css("span.field-content *::text").extract()
                    coreqs = process_course_requirements(text, course_code)
                    coreq_text = ''.join(text)
                except (AttributeError, IndexError):
                    coreqs = ''
                    coreq_text = ''

                try:
                    text = row.css("span.views-field.views-field-field-recommended").css("span.field-content *::text").extract()
                    prep = process_course_requirements(text, course_code)
                    prep_text = ''.join(text)
                except (AttributeError, IndexError):
                    prep = ''
                    prep_text = ''

                try:
                    distribution = row.css("span.views-field.views-field-field-distribution-requirements").css("span.field-content *::text").extract()
                except (AttributeError, IndexError):
                    distribution = []

                try:
                    breadth = row.css("span.views-field.views-field-field-breadth-requirements").css("span.field-content *::text").extract()
                except (AttributeError, IndexError):
                    breadth = []

                try:
                    mode_of_delivery = row.css("span.views-field.views-field-field-method-of-delivery").css("span.field-content *::text").extract()
                except (AttributeError, IndexError):
                    mode_of_delivery = []

                try:
                    text = row.css("span.views-field.views-field-field-exclusion").css("span.field-content *::text").extract()
                    exclusions = process_course_requirements(text, course_code)
                    exclusion_text = ''.join(text)
                except (AttributeError, IndexError):
                    exclusions = ''
                    exclusion_text = ''

                yield {
                    "course name": course_name,
                    "hours": hours,
                    "description": description,
                    "prerequisites": prereqs,
                    "corequisites": coreqs,
                    "prep": prep,
                    "distribution": distribution,
                    "breadth": breadth,
                    "mode of delivery": mode_of_delivery,
                    "exclusions": exclusions,
                    "prereq text": prereq_text,
                    "coreq text": coreq_text,
                    "exclusion text": exclusion_text,
                    "prep text": prep_text,
                    "course code": course_code
                }


def process_course_requirements(requirements: list[str], curr_course: str) -> str:
    """
    Function that takes course requirements as displayed on the website and parses them into a uniform format

    Course requirement format:
    () are used to group requirements together
    Separators:
    - ^ means "and"
    - | means "or"

    Logically, the operator hierarcy is () -> | -> ^
    """
    out = ""
    for line in requirements:
        if is_course_format(line) and line != curr_course:
            # Add a requirement if it is a course, excluding the current course
            out += line
        else:
            # Replace separators represented as words/characters with symbols
            line = line.replace('++', '') # Some courses have ++ in requirements, should not be interpreted as "and"
            line = line.replace('+', '^')
            line = line.replace('; and', '^')
            line = line.replace('; or', '|')
            line = line.replace(', and', '^')
            line = line.replace(', or', '|')
            line = line.replace('and/or', '|')
            line = line.replace('and', '^')
            line = line.replace(';', '^')
            line = line.replace(',', '^')
            line = line.replace('/', '|')
            line = line.replace('or', '|')
            for i in line:
                if i in ('|', '^'):
                    out += i
    return out
def is_course_format(s: str) -> bool:
    """
    Helper function - Return whether a string is in the format of a course

    >>> is_course_format("CSC111H1")
    True
    >>> is_course_format("CSCAA1")
    False
    >>> is_course_format("")
    False
    """
    if len(s) == 8 and s[0:3].isalpha() and (s[3:6].isnumeric() or (s[4:6].isnumeric())) and s[
        6].isalpha() and \
            s[7].isnumeric():
        return True
    else:
        return False
