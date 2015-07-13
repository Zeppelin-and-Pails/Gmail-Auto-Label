#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gmail-auto-label start

automatically generates labels for use in gmail,
based on either sender address, or recipient address (use with catch all addresses)

@category   Utility
@version    $ID: 1.1.1, 2015-07-01 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""

import pprint

import re
import sys
import gmailconnector


def main():
    con = gmailconnector.gmailconnector()

    labels = {}

    for label in con.get_labels():
        labels[label['name']] = label['id']

    if not labels:
        print 'No labels found.'
    else:
        print '{0} labels found.'.format(len(labels))

        pprint.pprint(labels)

        messages = con.get_inbox_messages()

        if not messages:
            print 'No messages found.'
        else:
            msg = 0
            bad = 0
            for message in messages:
                try:
                    address = con.get_address(message['id'])
                    radd = re.search(r'(?<=<)(.+)(?=>)', address)
                    if radd:
                        address = radd.group(0)

                    label = re.sub(r'\.', '/', re.search(r'(.+)(?=@)', address).group(0))
                    if label not in labels:
                        print label
                        try:
                            con.add_label(label)
                            labels.append(label)
                        except:
                            bad += 1
                            pass

                    con.move_msg_to_label(message['id'], labels[label])
                    msg += 1
                except:
                    bad += 1

                updateCLI(msg, bad, len(messages))

    print '[DONE]'

def updateCLI(passed, error, total):
    # standard message
    sys.stdout.write("\r{0} of {1} messages processed; ".format(passed, total))
    # if there are errors lets put that on the cli too
    if error > 0:
        sys.stdout.write("{0} errors; ".format(error))
    # now push it all out to the cli
    sys.stdout.flush()


if __name__ == '__main__':
    main()
