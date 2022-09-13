import sys
import os
import re
import math
import operator

positive_score = 2
negative_score = 0
neutral_score = 1

def tokenizeText(originalString):
    result = []
    # do not tokenize acronyms and abbreviations while tokenizing '.'
    str1 = re.findall(r'[A-Za-z]+[.]+[A-Za-z][.A-Za-z]*', originalString)
    for s in str1:
        result.append(s)
    modifiedString = re.sub(r'[A-Za-z]+[.]+[A-Za-z][.A-Za-z]*', '', originalString)

    # do not tokenize numbers while tokenizing ','
    str2 = re.findall(r'[0-9]+[,]+[0-9][0-9]*', modifiedString)
    for s in str2:
        result.append(s)
    modifiedString = re.sub(r'[0-9]+[,]+[0-9][0-9]*', '', modifiedString)

    # do not tokenize numbers while tokenizing '.'
    str3 = re.findall(r'[0-9]+[.]+[0-9][0-9]*', modifiedString)
    for s in str3:
        result.append(s)
    modifiedString = re.sub(r'[0-9]+[.]]+[0-9][0-9]*', '', modifiedString)

    # expand when needed while tokenizing
    expansion_list = {}
    expansion_list["isn't"] = "is not"
    expansion_list["won't"] = "will not"
    expansion_list["you're"] = "you are"
    expansion_list["they're"] = "they are"
    expansion_list["she'd"] = "she had"
    expansion_list["he'd"] = "he had"
    expansion_list["I'd"] = "I had"
    expansion_list["we'll"] = "we will"
    expansion_list["you'll"] = "you will"
    expansion_list["I'll"] = "I will"
    expansion_list["she'll"] = "she will"
    expansion_list["he'll"] = "he will"
    expansion_list["he's"] = "he is"
    expansion_list["it's"] = "it is"
    expansion_list["she's"] = "she is"
    expansion_list["I'm"] = "I am"
    expansion_list["let's"] = "let us"
    result = []
    modifiedString = modifiedString.lower()
    str4 = re.findall(r"[A-Za-z]+'[A-Za-z]+", modifiedString)
    for s in str4:
        if s in expansion_list.keys():
            result.extend(expansion_list[s].split())
        else:
            a = re.split(r"'", s)
            a[1] = "'s"
            result.extend(a)
    modifiedString = re.sub(r"[A-Za-z]+'[A-Za-z]+", '', modifiedString)

    # keep dates together 03/22/2022
    str5 = re.findall(r'(\d{1,2})\/(\d{1,2})\/(\d{4})', modifiedString)
    for s in str5:
        result.append(s)
    modifiedString = re.sub(r'(\d{1,2})\/(\d{1,2})\/(\d{4})', '', modifiedString)

    # keep phrases separated by - together while tokenizing '-'
    str6 = re.findall(r'[A-Za-z0-9_]+-[A-Za-z0-9_]+[-[A-Za-z0-9_]+]*', modifiedString)
    for s in str6:
        result.append(s)
    modifiedString = re.sub(r'[A-Za-z0-9_]+-[A-Za-z0-9_]+[-[A-Za-z0-9_]+]*', '', modifiedString)

    # tokenize strings that are not poart of the special cases and add them to the result list
    tokens = modifiedString.split()
    for token in tokens:
        token = re.sub(r'\W+', '', token)
        if token == "":
            continue
        else:
            result.append(token)
    return result

def trainNaiveBayes(training_file: str):
    vocabulary = []
    # data structure with class probabilities (or log of probabilities);
    class_probabilities = {}
    class_probabilities['negative'] = 0
    class_probabilities['positive'] = 0
    class_probabilities['neutral'] = 0
    # data structure with word conditional probabilities (or log of probabilities);
    word_conditional_probabilities = {}
    word_conditional_probabilities['negative'] = {}
    word_conditional_probabilities['positive'] = {}
    word_conditional_probabilities['neutral'] = {}
    # data structure with occurances
    occurrences = {}
    number_negative_occurrences = 0
    number_positive_occurrences = 0
    number_neutral_occurrences = 0
    total_number_training_files = 0
    total_number_negative_files = 0
    total_number_positive_files = 0
    total_number_neutral_files = 0
    f = open(training_file)
    posts = f.readlines()
    f.close()
    for post in posts:
        total_number_training_files += 1
        if post[0] == '0':
            total_number_negative_files += 1
            if 'negative' not in occurrences.keys():
                occurrences['negative'] = {}
        elif post[0] == '4':
            total_number_positive_files += 1
            if 'positive' not in occurrences.keys():
                occurrences['positive'] = {}
        else:
            total_number_neutral_files += 1
            if 'neutral' not in occurrences.keys():
                occurrences['neutral'] = {}

        line = post[2:]
        line.strip()
        words = []
        if line != '':
            words = tokenizeText(line)
        for word in words:
            if word not in vocabulary:
                vocabulary.append(word)
            if post[0] == '0':
                if word in occurrences['negative'].keys():
                    occurrences['negative'][word] += 1
                else:
                    occurrences['negative'][word] = 1
            elif post[0] == '4':
                if word in occurrences['positive'].keys():
                    occurrences['positive'][word] += 1
                else:
                    occurrences['positive'][word] = 1
            else:
                if word in occurrences['neutral'].keys():
                    occurrences['neutral'][word] += 1
                else:
                    occurrences['neutral'][word] = 1
    for val1 in occurrences['negative'].keys():
        number_negative_occurrences += occurrences['negative'][val1]
    for val2 in occurrences['positive'].keys():
        number_positive_occurrences += occurrences['positive'][val2]
    for val3 in occurrences['neutral'].keys():
        number_neutral_occurrences += occurrences['neutral'][val3]
    class_probabilities['negative'] = math.log10(total_number_negative_files / total_number_training_files)
    class_probabilities['positive'] = math.log10(total_number_positive_files / total_number_training_files)
    class_probabilities['neutral'] = math.log10(total_number_neutral_files / total_number_training_files)
    # vocabulary size
    vocabulary_size = len(vocabulary)
    for voc in vocabulary:
        if voc in occurrences['negative'].keys():
            word_conditional_probabilities['negative'][voc] = math.log10(
                (occurrences['negative'][voc] + 1) / (number_negative_occurrences + vocabulary_size))
        if voc in occurrences['positive'].keys():
            word_conditional_probabilities['positive'][voc] = math.log10(
                (occurrences['positive'][voc] + 1) / (number_positive_occurrences + vocabulary_size))
        if voc in occurrences['neutral'].keys():
            word_conditional_probabilities['neutral'][voc] = math.log10(
                (occurrences['neutral'][voc] + 1) / (number_neutral_occurrences + vocabulary_size))
    return class_probabilities, word_conditional_probabilities, vocabulary_size, number_negative_occurrences, number_positive_occurrences, number_neutral_occurrences

def testNaiveBayes(path, class_probabilities, word_conditional_probabilities, vocabulary_size, number_negative_occurrences, number_positive_occurrences, number_neutral_occurrences):

    classification = []

    f = open(path, 'r', encoding="ISO-8859-1")
    Lines = f.readlines()
    for line in Lines:
        predicted = {}
        predicted['negative'] = class_probabilities['negative']
        predicted['positive'] = class_probabilities['positive']
        predicted['neutral'] = class_probabilities['neutral']
        line.strip()
        if line != '':
            words = []
            words = tokenizeText(line)
            for word in words:
                # The tokens that are not in the vocabulary should have smoothing applied.
                if word in word_conditional_probabilities['negative'].keys():
                    predicted['negative'] += word_conditional_probabilities['negative'][word]
                else:
                    predicted['negative'] += math.log10(1 / (number_negative_occurrences + vocabulary_size))
                if word in word_conditional_probabilities['positive'].keys():
                    predicted['positive'] += word_conditional_probabilities['positive'][word]
                else:
                    predicted['positive'] += math.log10(1 / (number_positive_occurrences + vocabulary_size))
                if word in word_conditional_probabilities['neutral'].keys():
                    predicted['neutral'] += word_conditional_probabilities['neutral'][word]
                else:
                    predicted['neutral'] += math.log10(1 / (number_neutral_occurrences + vocabulary_size))
        if predicted['negative'] > predicted['positive'] and predicted['negative'] > predicted['neutral']:
            classification.append('negative')
        elif predicted['positive'] > predicted['negative'] and predicted['positive'] > predicted['neutral']:
            classification.append('positive')
        else:
            classification.append('neutral')
    return classification

# python3 naivebayes.py course-info redditcrawl_Courses testdata.manual.2009.06.14.csv
def main():
    course_sentiment = {}
    course_info = str(sys.argv[1])
    redditcrawl_Courses = str(sys.argv[2])
    train_set = str(sys.argv[3])
    course_path = os.path.join(os.getcwd(), redditcrawl_Courses)

    # training with the test data set
    class_probabilities, word_conditional_probabilities, vocabulary_size, \
        number_negative_occurrences, number_positive_occurrences, number_neutral_occurrences = trainNaiveBayes(train_set)

    # test the feedbacks of each course
    # get a list of the sentiment classification for each course
    for course_file in os.listdir(course_path):
        course_list = testNaiveBayes(course_path + course_file, class_probabilities,
                       word_conditional_probabilities, vocabulary_size, number_negative_occurrences,
                       number_positive_occurrences, number_neutral_occurrences)
        course_name = course_file.split('.')[0]
        course_sentiment[course_name] = course_list

    # read the atlas score
    f = open(course_info, 'r')
    infos = f.readlines()
    f.close()

    course_score = {}

    # calculate the score:
    # score = (#positive - #negative) / #All_feedbacks * atlas_weight
    for info in infos:
        temp = info.split(':')
        course_name = temp[0]
        course_weight = temp[1].strip()
        if course_weight == 'N/A':
            continue
        try:
            if len(course_sentiment[course_name]) == 0:
                continue
        except KeyError:
            continue

        course_score[course_name] = 0
        for classification in course_sentiment[course_name]:
            if classification == 'negative':
                course_score[course_name] += negative_score
            elif classification == 'positive':
                course_score[course_name] += positive_score
            else:
                course_score[course_name] += neutral_score
        course_score[course_name] /= len(course_sentiment[course_name])

        course_score[course_name] *= float(course_weight)

    # sort the result and print out
    course_score_sorted = dict(sorted(course_score.items(), key=operator.itemgetter(1), reverse=True))

    for course in course_score_sorted:
        print(course, end=' ')
        print(course_score_sorted[course])
        print(course_sentiment[course])

if __name__ == "__main__":
    main()