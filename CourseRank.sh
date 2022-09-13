#!/bin/sh

# Step 1: crawl Atlas with seed URLs stored in atlas_seeds,
#         outputs course-info with all courses and their atlas score
# username: replaced by your umich username
# password: replaced by your umich password
python3 atlas_crawler.py all_atlas_links 12632 <username> <password>

# Step 2: crawl Reddit with the course list in course-info
#         outputs a set of files in redditcrawl_Courses
#         each one contains the related feedbacks found on Reddit
python3 reddit.py course-info

# Step 3: use naivebayes algorithm to classify all feedbacks
#         assign a score to each feedback
#         calculate the overall score for each course
#         times the atlas score as the weight
python3 naivebayes.py course-info courseReddit/ testdata.manual.2009.06.14.csv > score.out
