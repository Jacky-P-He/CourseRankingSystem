import praw
import sys
import pathlib
import os

def main():
    # Define user agent
    user_agent = "praw_scraper_1.0"

    # Create an instance of reddit class
    reddit = praw.Reddit(
        client_id="Q6WYrm5jdH2o9IQBLffzXg",
        client_secret="rIAxLDKTC8mktIFlY5ON1EmqxhjDXA",
        user_agent=user_agent
    )

    # Create sub-reddit instance
    subreddit_name = "uofm"
    subreddit = reddit.subreddit(subreddit_name)

    # Store course comments in dict, store course name in courseList
    dict = {}
    courseList = []
    filename = sys.argv[1]

    # Get course information from the file course-info
    with open(filename, 'r') as ci:
        tempList = ci.readlines()
    ci.close()

    # Extract only course name
    for i in tempList:
        if 'N/A' in i:
            continue
        courseList.append(i.split(':')[0])

    # Get comments for each course
    for i, course_name in enumerate(courseList):
        course_name = course_name[:-3] + ' ' + course_name[-3:]
        print(str(i + 1) + ' ' + course_name)

        # Get related URL for each course
        urls = []
        for submission in subreddit.search(course_name):
            urls.append(submission.url)

        dict[course_name] = []
        num = 0

        for url in urls:
            try:
                # Get comments from links
                # The maximum is 30 posts
                if num == 30:
                    break
                print("EXPLORING ", url)
                submission = reddit.submission(url=url)
                for comment in submission.comments:
                    if comment.body != '':
                        dict[course_name].append(comment.body)
                        print(comment.body)
                num += 1
                print('----------------------------------------')
            except Exception:
                continue

    reddit_dir = pathlib.Path('courseReddit/')
    if not os.path.isdir(reddit_dir):
        os.mkdir(reddit_dir)

    # Output the files into a folder
    for key, value in dict.items():
        if value:
            course = key[:-4] + key[-3:]
            output = open('courseReddit/' + course + '.txt', 'w')
            for i in value:
                output.write(i + '\n')
            output.close()


if __name__ == "__main__":
    main()
