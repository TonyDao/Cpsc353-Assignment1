#!/usr/bin/env python
import sys
import string

GROUPENUM = []
USERENUM = []
OBJECTNUM = []
ACCESSRIGHT = ["execute", "write", "read"]
USERGROUPMATRIX = []
PERMISSIONMATRIX = []

def usage(scriptname):
    msg = 'Usage: %s <group file> <resources file> <attempts file>' % scriptname
    sys.exit(msg)

# create group enumerate, user enumerate, and matrix of group(row) by user(column)
def groups (filename):
    global USERGROUPMATRIX
    result = []
    with open(filename) as f:
        for cleartext in f:
            line = cleartext.rstrip('\n')
            # split group and users
            word = line.split(': ', 1)
            word[1] = word[1].split(', ')
            # save group and user into array
            result.append(word)
            # add group into group enumerate
            GROUPENUM.append(word[0])
            # add user into user enumerate with 
            [USERENUM.append(user) for user in word[1] if user not in USERENUM]

    # Init matrix group(row) by user(column)
    matrix = [[False] * len(USERENUM) for _ in range(len(GROUPENUM))]

    # True for correct user in the group
    for group, users in result:
        for user in users:
            row = GROUPENUM.index(group)
            column = USERENUM.index(user)
            matrix[row][column] = True

    # add matrix to global USERGROUPMATRIX
    USERGROUPMATRIX = matrix
    # print "GROUPENUM: %s" % GROUPENUM
    # print "USERENUM: %s" % USERENUM
    # print "USERGROUPMATRIX: %s" % USERGROUPMATRIX

# convert permission into number (read - 4, write - 2, execute - 1)
def convertPermToNum(perms):
    total = 0
    index = 0
    for perm in perms.split(', '):
        # add permission to list
        if perm not in ACCESSRIGHT:
            ACCESSRIGHT.append(perm)

        # get index of permission
        index = ACCESSRIGHT.index(perm)
        # set bit of pecific index
        total = total | (2**index)

    return total

# create object enumerate and permission maxtrix of group(row) x object(column)
def resources (filename):
    row = [0] * len(GROUPENUM)
    with open(filename) as f:
        for cleartext in f:
            
            line = cleartext.rstrip('\n')
            words = line.split(':')

            # check not empty
            if ':' in line:
                # check group inside of object
                if line[:4] == "    ":
                    group = words[0][4:]
                    perm = words[1][1:]
                    # add permission number into correct position in matrix
                    row[GROUPENUM.index(group)] = convertPermToNum(perm)
                # object
                else:
                    # add object into object enumerate
                    OBJECTNUM.append(words[0])
            # end of an object
            else:
                # append row into maxtrix
                PERMISSIONMATRIX.append(row)
                # restore default empty row
                row = [0] * len(GROUPENUM)

    # append last row into maxtix
    PERMISSIONMATRIX.append(row)
    # print "OBJECTNUM: %s" % OBJECTNUM
    # print "PERMISSIONMATRIX: %s" % PERMISSIONMATRIX

# check permission according to the permission
def checkUserAction(action, permission):
    # print "permission: %s" % permission
    if action in ACCESSRIGHT:
        index = (ACCESSRIGHT.index(action) + 1) * -1
        binaryPerm = bin(permission)[2:].zfill(len(ACCESSRIGHT))
        # print "bin: %s and index: %s" % (binaryPerm, index)
        # print binaryPerm[index]
        if binaryPerm[index] == '1':
            return True
    
    return False

# process Attempted actions
def attempts (filename):
    global USERGROUPMATRIX
    with open(filename) as f:
        for cleartext in f:
            line = cleartext.rstrip('\n')
            sub, action, obj = line.split(' ')

            # check object, subject, and action
            if obj in OBJECTNUM and sub in USERENUM and action in ACCESSRIGHT:
                # get all the groups that user is in
                groups = []
                for group in GROUPENUM:
                    row = GROUPENUM.index(group)
                    column = USERENUM.index(sub)
                    if USERGROUPMATRIX[row][column]:
                        groups.append(row)

                # union user Permission base object on permission matrix
                unionPerm = 0
                for group in groups:
                    unionPerm = unionPerm | PERMISSIONMATRIX[OBJECTNUM.index(obj)][group]

                # print result of user action permission
                if checkUserAction(action, unionPerm):
                    print "ALLOW %s" % line
                else:
                    print "DENY %s" % line

            # can't find object permission
            else:
                print "DENY %s" % line


if __name__ == '__main__':

    if len(sys.argv) != 4:
        usage(sys.argv[0])

    groups(sys.argv[1])
    resources(sys.argv[2])
    attempts(sys.argv[3])