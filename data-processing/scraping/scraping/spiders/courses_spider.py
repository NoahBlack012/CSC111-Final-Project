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
        curr_course = None
        for n, row in enumerate(response.css("div.views-row")):
            if n % 2 == 0:
                curr_course = row.css("h3.js-views-accordion-group-header::text").extract()[0].strip()
            else:
                # Corequisites and prerequisites are strings to represent possible combinations or corequisites or
                # prerequisites. ^ represents and (A^B means that the prerequisites of a course are both A and B)
                #. | represents or (A|B means that the prerequisites of a course are either A or B)
                course_info = {
                    "hours": None,
                    "description": '',
                    "prerequisites": "",
                    "corequisites": "",
                    "distribution": '',
                    "breadth": '',
                    "method of delivery": None,
                    "exclusions": []
                }
                text = row.css("::text").getall()
                current_item = None
                for line_num, line in enumerate(text):
                    line_s = line.strip()
                    if line_s == "":
                        continue
                    elif line_s == "Hours:":
                        current_item = "hours"
                    elif line_num == 1 and text[1].strip() != "Hours:":
                        current_item = "description"
                    elif line_s == "Prerequisite:":
                        current_item = "prerequisites"
                    elif line_s == "Corequisite:":
                        current_item = "corequisites"
                    elif line_s == "Exclusion:":
                        current_item = "exclusions"
                    elif line_s == "Distribution Requirements:":
                        current_item = "distribution"
                    elif line_s == "Breadth Requirements:":
                        current_item = "breadth"
                    elif line_s == "Mode of Delivery:":
                        current_item = "mode of delivery"
                    else:
                        # If the current row represents a piece of information
                        if current_item == "hours":
                            course_info["hours"] = line_s
                            # Description always follows course hours
                            current_item = "description"
                        elif current_item == "description":
                            course_info["description"] += line_s
                            current_item = None
                        elif current_item == "prerequisites":
                            if len(line_s) == 8:
                                # A line may consist of just a comma, course codes have 8 characters
                                course_info["prerequisites"] += line_s
                            else:
                                # Look for separators in line - , / ( ) ;
                                for i in line_s:
                                    if i == "(" or i == ")":
                                        course_info["prerequisites"] += i
                                    if i == "," or i == ";":
                                        course_info["prerequisites"] += "^"
                                    if i == "/":
                                        course_info["prerequisites"] += "|"
                        elif current_item == "corequisites":
                            if len(line_s) == 8:
                                # A line may consist of jsut a comma, course codes have 8 characters
                                course_info["corequisites"] += line_s
                            else:
                                # Look for separators in line - , / ( ) ;
                                for i in line_s:
                                    if i == "(" or i == ")":
                                        course_info["corequisites"] += i
                                    if i == "," or i == ";":
                                        course_info["corequisites"] += "^"
                                    if i == "/":
                                        course_info["corequisites"] += "|"
                        elif current_item == "exclusions":
                            course_info["exclusions"].append(line_s)
                            current_item = None
                        elif current_item == "distribution":
                            course_info["distribution"] = line_s
                            current_item = None
                        elif current_item == "breadth":
                            course_info["breadth"] = line_s
                            current_item = None
                        elif current_item == "mode of delivery":
                            course_info["mode of delivery"] = line_s
                            current_item = None
                yield {
                    "course name": curr_course,
                    "hours": course_info["hours"],
                    "description": course_info["description"],
                    "prerequisites": course_info["prerequisites"],
                    "corequisites": course_info["corequisites"],
                    "distribution": course_info["distribution"],
                    "breadth": course_info["breadth"],
                    "mode of delivery": course_info["mode of delivery"],
                    "exclusions": course_info["exclusions"]
                }
