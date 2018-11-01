import argparse
import html5lib
from collections import OrderedDict
import sys

TABLE = '{http://www.w3.org/1999/xhtml}table'
TBODY = '{http://www.w3.org/1999/xhtml}tbody'
TR = '{http://www.w3.org/1999/xhtml}tr'
TD = '{http://www.w3.org/1999/xhtml}td'

DAYS = ['pondělí', 'úterý', 'středa', 'čtvrtek', 'pátek', 'sobota']

sh = OrderedDict(sorted({0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}.items(), key=lambda t: t))

def parse_lecture(td):
    hours = int(td.attrib['colspan'])
    tables = td.findall(TABLE)
    #print('Lecture:', table)
    table_lecture = tables[0]

    tbody = table_lecture.find(TBODY)
    tr = tbody.find(TR)
    td = tr.find(TD)
    lecture_name = td.text
    print(lecture_name, end=' ')

    table_room = tables[1]
    tbody = table_room.find(TBODY)
    tr = tbody.find(TR)
    td = tr.find(TD)
    lecture_room = td.text

    table_type_and_groups = tables[2]
    tbody = table_type_and_groups.find(TBODY)
    tr = tbody.find(TR)
    tds = tr.findall(TD)
    lecture_type = tds[0].text
    lecture_groups = tds[1].text
    lecture_recitation_exercise, lecture_no = lecture_type.split('/')
    
    lecture = Lecture(lecture_name, lecture_room, lecture_recitation_exercise, lecture_no, lecture_groups, hours)

    return hours, lecture


class Lecture:

    def __init__(self, name, room, lecture_type, lecture_no, study_group, hours):
        self.name = name
        self.room = room
        self.lecture_type = lecture_type
        self.lecture_no = lecture_no
        self.study_group = study_group
        self.hours = hours

    @staticmethod
    def from_td(td):
        return parse_lecture(td)


def print_schedule(hour_list, sh):
    for hour in hour_list:
        print(hour, end=' ')
    for day_no in sh:
        for no, hour in enumerate(sh[day_no]):
            l = len(hour_list[no])
            s = ''.rjust(l//2) + hour + ''.ljust(l//2)
            print(s, end=' ')
        print()


def main():

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('filename', metavar='filename', type=str, nargs='+',
                        help='filename with HTML timetable')
    
    args = parser.parse_args()
    print(args.filename)

    hour_list = []

    with open(args.filename[0], 'rb') as f:
        doc = html5lib.parse(f)
        print(doc)
        body = doc.find('{http://www.w3.org/1999/xhtml}body')
        print(body)
        print()
        for e in body:
            if e.tag == '{http://www.w3.org/1999/xhtml}table':
                #print(e)
                #print(e.attrib)
                cl = e.attrib['class']
                if cl == 'grid-border-args':
                    tbody = e.find('{http://www.w3.org/1999/xhtml}tbody')
                    for day_no, row in enumerate(tbody.findall('{http://www.w3.org/1999/xhtml}tr')):
                        #print(row)
                        # for each time slot
                        for col_no, td in enumerate(row.findall('{http://www.w3.org/1999/xhtml}td')):
                            #print(td.text)
                            #print(sh)
                            if 'class' in td.attrib:
                                cl = td.attrib['class']
                                if cl == 'col-label-one' or cl == 'row-label-one':
                                    text = td.text if td.text else '       '
                                    if text in DAYS:
                                        max_day_len = max([ len(s) for s in DAYS])
                                        print(td.text + ''.rjust(max_day_len - len(text)) + ': ', end=' ')
                                    else:
                                        hour_list.append(td.text)
                                        print(td.text, end=' ')
                                # actual lecture
                                elif cl == 'object-cell-border':
                                    #print('HODINA')
                                    hours, lecture = parse_lecture(td)
                                    for i in range(hours):
                                        sh[day_no].append('X')
                                else:
                                    # empty
                                    sh[day_no].append('O')
                            else:
                                print('       ')
                        print()

    print()

    print_schedule(hour_list, sh)


if __name__ == '__main__':
    main()


#import requests

#r = requests.get('https://rozvrh.vsb.cz/Reporting/Individual?idtype=id&objectclass=staff&weeks=1-14&identifier=GAU01&template=VyucujiciNaz', auth=('user', 'pass'))

#print(r.text)
