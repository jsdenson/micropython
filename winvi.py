#
# Attempting to make a simple editor for micropython
#
'''
Feature set working:

    if key == 0:    # move to begin of line
    if key == $:    # move to end of line
    if key == ESC:  # command mode from insert,append, etc...
    if key == ':':  # os command: e w q
    if key == '.':  # repeat last edit command - not navigation, not search, and not os command
    if key == 'a':  # append chars after current until ESC
    if key == 'b':  # move to begin of a word - move prev line TBD
    if key == 'c'+w: # change word - num d not supported
    if key == 'd'+d: # del line - num d not supported
    if key == 'd'+w: # del word - num d not supported
    if key == 'D':  # delete rest of line
    if key == 'e':  # move to end of a word - move next line TBD
    if key == 'G':  # go to stored number or end if no number
    if key == 'h':  # left
    if key == 'j':  # down
    if key == 'J':  # join 2 lines
    if key == 'k':  # up
    if key == 'l':  # right
    if key == 'i':  # insert chars until ESC TBD
    if key == 'o':  # insert line(s) after current until ESC
    if key == 'O':  # insert line(s) before current until ESC
    if key == 'p':  # paste append line or word depending on last 'y' command
    if key == 'P':  # paste insert line or word depending on last 'y' command
    if key == 'r':  # replace char TBD
    if key == 'R':  # replace chars until ESC
    if key == 's':  # overwrite char and insert until ESC
    if key == 'w':  # move to begin of next word
    if key == 'y'+y:  # yank line
    if key == 'y'+w:  # yank word
    if key == '/':  # search down
    if key == '?':  # search up
    if key == 'n':  # repeat last search in last direction
    if key == 'u':  # undo last edit - still WIP TBD ... history should be updated if a new command replaces old
    if key == 'U':  # redo last edit - still WIP TBD ... history should be updated if a new command replaces old
    if key == CTRL+R:  # redo last edit
    if key == CTRL+C:  # abort
    if key == CTRL+G:  # get file name, line, column, etc...
    if key == CTRL+L:  # refresh screen
    if key == CTRL+D:  # page down
    if key == CTRL+B:  # page up
    if key == CTRL+F:  # page down
    if key == CTRL+P:  # page up
    if key == numeric and first char != 0 store number until command

Feature set TBD:
    if key == 'c':  # cw, ce, c$ ?

'''

import os
import sys

'''
print raw
'''
def printr(text):

    #print(text, end='')
    sys.stdout.write(text)
    sys.stdout.flush()


class edhist:

    cmd : str = ""
    last_cmd: str = ""
    txt : str = ""
    x : int = 0
    y : int = 0
    nx : int = 0
    ny : int = 0
    incr : int = 0


class editor:

    g_version = 0.1

    g_by: int = 0    # begin line/row of window
    g_cli_line: int = 30 # end of line/row window

    g_sx: int = 0    # current char x col position
    g_sy: int = 0    # current char y row position

    g_nx: int = 0    # max x position number of chars
    g_ny: int = 0    # max y position number of lines

    g_cmd: bool = True
    g_cmd_key: str = ''
    g_fn: str = ""

    g_history_ndx = 0
    g_last_cmd: str = ""
    g_command_start = False
    g_command_replay: int = 0

    g_nums = ''
    g_number = 0

    g_search_dir = 0
    g_search_string = ''

    g_yanked = ''
    g_yankline = ''
    g_yankword = ''

    YANK_LINE = 'y'
    YANK_WORD = 'w'

    CTL_B = 2
    CTL_C = 3
    CTL_G = 7
    CTL_L = 12
    CTL_R = 18
    CTL_ESC = 0x1b
    CTL_D = 4
    CTL_F = 6
    CTL_P = 16
    CTL_U = 21

    esc_clrscr = "\33[2J\33[H"

    esc_curstop = "\33[H"
    esc_cursbot = "\33[{}B"
    esc_cursline = "\33[H\33[{}B"
    esc_cursxpos = "\r\33[{}C"

    esc_cursup = "\33[A"
    esc_cursdn = "\33[B"
    esc_curslt = "\33[D"
    esc_cursrt = "\33[C"


    def __init__(self):

        self.g_buf = []
        self.g_bufprev = [] # for diffing buf
        self.g_bufnew  = [] # virgin buf
        self.g_history = [] # commands applied to virgin buf

        try:
            import usys
            self.g_cli_line = 40
        except:
            pass


        print("uedit v{:f}".format(self.g_version))


    def appendchars(self, index):

        self.insertchars(index+1)


    def appendline(self, ln):

        self.g_buf.append(ln)
        self.g_sx = 0
        printr(ln)


    def bottom(self):

        printr(self.esc_curstop)
        printr(self.esc_cursbot.format(self.g_cli_line + 1))


    def charat(self, X, Y):

        if len(self.g_buf) > Y:
            try:
                E = len(self.g_buf[Y])
                return self.g_buf[Y][X] if X < E else ''
            except:
                return ''
        else:
            return ''


    def clear(self):

        try:
            # normal version
            #printr(self.esc_clrscr)
            os.system("clear")

        except:
            pass

        printr(self.esc_clrscr)

        clear = ''
        for j in range(self.g_nx):
            clear += ' '
        for j in range(self.g_cli_line+1):
            print(clear)

        printr(self.esc_clrscr)


    def deletechar(self):

        if not len(self.g_buf):
            return

        # del char position
        index = self.g_sx
        oldlen = len(self.g_buf[self.g_sy])
        # new buf without char
        buf = self.g_buf[self.g_sy]
        if not len(buf):
            return
        b1 = buf[:index]
        b2 = buf[index + 1:]
        buf = b1 + b2
        # replace old with new
        self.g_buf.pop(self.g_sy)
        self.g_buf.insert(self.g_sy, buf)
        # set new index
        self.g_sx = index - 1
        # replace old on screen contents
        ln = buf[index:-1]
        printr(ln)
        # erase last char
        printr(' ')
        lnlen = len(self.g_buf[self.g_sy]) - 2
        if self.g_sx < lnlen:
            self.g_sx += 1
        self.status()


    def deleteline(self, count=1):

        if not len(self.g_buf):
            return

        if count == 1:
            self.g_yankline = self.g_buf.pop(self.g_sy)
            self.g_yanked = self.YANK_LINE
            self.g_ny -= 1

        else:
            for j in range(count):
                self.g_buf.pop(self.g_sy)
                self.g_ny -= 1

        self.refresh()


    '''
    deletes word at cursor.
    a word is something separated by spaces.
    so, 'hello,' and the comma would be deleted. 
    not exactly what vim does.
    '''
    def deleteword(self, count=1):

        if not len(self.g_buf):
            return

        line = ""
        buf = self.g_buf[self.g_sy]
        if not len(buf):
            return
        rmx = self.g_sx
        #if self.g_buf[rmx] == ' ': rmx += 1
        lb1 = buf[:rmx]
        lb2 = lb1
        while rmx < len(buf):
            # maybe add ',;:' as delimiters?
            if buf[rmx].isspace() or buf[rmx] == ',' or buf[rmx] == ';' or buf[rmx] == ':':
                rmx += 1
                lb2 = buf[rmx:]
                break
            rmx += 1
        line = lb1+lb2
        if not len(line):
            line += '\n'

        self.g_buf.pop(self.g_sy)
        self.g_buf.insert(self.g_sy, line)

        count -= 1
        if count > 0:
            self.deleteword(count)

        self.refreshline()


    def deletelinetoend(self):

        buf = self.g_buf[self.g_sy]
        if not len(buf):
            return
        X = self.g_sx
        buf = buf[:X]
        buf += '\n'
        self.g_buf.pop(self.g_sy)
        self.g_buf.insert(self.g_sy, buf)
        self.g_sx = len(buf)-2
        self.show(self.g_sy)
        self.refreshline()


    def gotowordend(self):

        y = self.g_sy
        if y >= self.g_ny:
            return

        line = self.g_buf[y]
        if not len(line):
            return
        x = self.g_sx
        if x < 0:
            x = self.g_sx = 0
        find = False
        while x < len(line):
            if find and self.charat(x, y).isspace():
                if x - 1 > 0:
                    self.g_sx = x - 1
                break
            if not self.charat(x + 1, y).isspace():
                find = True
            self.g_sx = x
            self.status()
            x += 1
            if len(line) and x == len(line) and y+1 < self.g_ny:
                x = 0
                y += 1
                self.g_sx = x
                self.g_sy = y
                line = self.g_buf[y]
                self.status()
        self.refreshline()


    def gotowordbegin(self):

        cnt = 0
        y = self.g_sy
        x = self.g_sx
        if x == 0:
            if self.g_sy > 0:
                self.g_sy -= 1
                y = self.g_sy
            x = len(self.g_buf[y]) - 1
        while x > -1:
            if self.charat(x, y).isspace():
                cnt += 1
                if cnt > 1:
                    break
            self.g_sx = x
            self.status()
            x -= 1

        self.status()


    def gotowordnext(self):

        y = self.g_sy
        if y >= self.g_ny:
            return

        line = self.g_buf[y]
        if not len(line):
            return
        x = self.g_sx
        if x < 0:
            x = self.g_sx = 0

        while x < len(line):
            if self.charat(x, y).isspace():
                break
            x += 1

        while x < len(line):
            if not self.charat(x, y).isspace():
                self.g_sx = x
                self.status()
                break
            x += 1
            if  x == len(line) and y+1 < self.g_ny:
                x = 0
                y += 1
                self.g_sx = x
                self.g_sy = y
                line = self.g_buf[y]
                self.status()


    def insertnewline(self, after):

        # add a temporary new line
        buf = '\n'
        self.g_sx = 0
        self.g_sy += after
        self.g_buf.insert(self.g_sy, buf)
        self.g_ny += 1
        self.show()


    def insertline(self, after):

        if not len(self.g_buf):
            after = 0

        self.insertnewline(after)

        # restart buffer
        buf = ''
        while True:

            ch = self.getkey()
            key = 0
            try:
                key = ord(ch)
            except:
                pass

            # for now just clobber \t - TBD handle better later
            if ch == '\t':
                ch = ' '

            if not key or key == self.CTL_ESC:
                #buf = str(buf).lstrip(1)
                buf += '\n'
                # replace line
                self.g_buf.pop(self.g_sy)
                self.g_buf.insert(self.g_sy, buf)
                break

            elif ch == '\b':
                buf = buf[:-1]
                self.g_sx -= 1
                self.status()

            elif ch == '\n' or ch == '\r':
                self.g_buf.pop(self.g_sy)
                buf += '\n'
                self.g_buf.insert(self.g_sy, buf)
                self.insertnewline(1)
                buf = ''

            else:
                printr(ch)
                buf += ch
                self.g_sx += 1

            self.status()

        self.show()
        self.status()


    def insertchars(self, index):

        if not len(self.g_buf):
            self.g_buf.append('\r')
            self.g_ny = 1
            self.g_nx = 40
            index = 0

        buf = self.g_buf[self.g_sy]
        lb1 = buf[:index]
        lb2 = buf[index:]
        wrd = ''

        printr('\r')
        for j in range(len(lb1)):
            printr(lb1[j])

        self.g_sx = index

        while True:

            ch = self.getkey()
            key = 0
            try:
                key = ord(ch)
            except:
                pass

            # for now just clobber \t - TBD handle better later
            if ch == '\t':
                ch = ' '

            if not key or key == self.CTL_ESC:
                buf = lb1+wrd+lb2
                if buf == '':
                    self.show()
                    self.status()
                    break
                if buf[-1] != '\n':
                    buf += '\n'
                self.g_sx += len(wrd)
                self.g_buf.pop(self.g_sy)
                self.g_buf.insert(self.g_sy, buf)
                cnt = len(buf)
                if cnt > self.g_nx:
                    self.g_nx = cnt+1
                self.show()
                self.status()
                break

            elif ch == '\b':
                wrd = wrd[:-1]
                printr(self.esc_curslt)
                printr(' ')
                printr(self.esc_curslt)

            elif ch == '\n' or ch == '\r':
                wrd += '\n'
                buf = lb1+wrd
                #self.g_sx += len(wrd)
                self.g_buf.pop(self.g_sy)
                self.g_buf.insert(self.g_sy, buf)
                self.insertnewline(1)
                if lb2.find('\n') > -1:
                    lb2 = lb2[:-1]
                lb1 = lb2
                lb2 = ''
                wrd = ''
                printr(lb1)

            else:
                wrd += ch
                printr(ch)
                ln = lb2[0:-1]
                printr(ln)
                for j in range(len(ln)):
                    printr(self.esc_curslt)


    '''
    micropython does not support str.isnumeric()
    '''
    def isnumeric(self, val):
        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        if val in numbers:
            return True
        return False

    def isalnumeric(self, val):
        try:
            if str(val).isalpha() or self.isnumeric(val):
                return True
        except:
            pass
        return False


    '''
    TBD replace with python str.isspace() ?
    '''
    def isspace(self, s):

        if s == ' ' or s == '\r' or s == '\n' or s == '\t':
            return True
        return False


    def joinlines(self):

        Y = self.g_sy
        if Y < self.g_ny:
            buf = self.g_buf[Y]
            if buf[-1] == '\n':
                buf = buf[:-1]
                buf += ' '
            buf += self.g_buf[Y + 1]
            self.g_buf.pop(Y + 1)
            self.g_buf.pop(Y)
            self.g_buf.insert(self.g_sy, buf)
            self.g_ny -= 1
            if len(buf) > self.g_nx:
                self.g_nx = len(buf)
            self.show()
            self.status()


    def pasteline(self, after=1):

        Y = self.g_sy + after
        buf = self.g_yankline
        if len(buf) > 0:
            self.g_sx = 0
            self.g_buf.insert(Y, buf)
            self.g_ny += 1
            self.show()
            self.status()


    def pasteword(self, after=1):
        word = self.g_yankword
        word = self.trim(word)
        if len(word):
            Y = self.g_sy
            buf = self.g_buf[Y]
            buf = self.trim(buf)
            lb1 = buf[:self.g_sx+after]
            lb2 = buf[self.g_sx+after:]
            buf = lb1 + word + ' ' + lb2
            '''
            if after > 0:
                buf = lb1 + word + ' ' + lb2
            else:
                buf = lb1 + ' ' + word + lb2
            '''
            buf += '\n'
            self.g_buf.pop(Y)
            self.g_buf.insert(Y, buf)
            self.show()
            self.status()


    def pathexists(self, path):
        try:
            os.stat(path)
        except OSError:
            return False
        return True


    def println(self, line):

        cnt = len(line)
        printr(line)
        self.g_sx += cnt
        self.g_sy += 1


    def rdfile(self, fname):

        # print("RdFile "+str(fname))
        with open(fname, 'r') as f:
            return f.readlines()


    def refresh(self):

        self.clear()
        nx = 40
        for j in range(self.g_cli_line):
            y = j + self.wintop()
            if y < self.g_ny:
                printr(self.g_buf[y])
                if len(self.g_buf[y]) > nx:
                    nx = len(self.g_buf[y])
            else:
                printr("~\n")
        self.g_nx = nx

        self.g_cmd = True
        self.status()


    def refreshline(self):

        buf = self.g_buf[self.g_sy]
        printr('\r')
        count = self.g_nx
        if count < len(buf):
            count = len(buf)
        for j in range(count):
            printr(' ')
        printr('\r'+buf)
        self.status()


    def searchdown(self, cmd):

        sp = cmd.split(' ')

        if len(sp) < 1:
            self.g_search_string = ''
            self.status('Search parameter not specified. Try again.')

        else:
            findstr = ""
            for j in range(len(sp)):
                #if j == 0: continue
                findstr += sp[j] + ' '

            if findstr[-1].isspace():
                findstr = findstr[:-1]

            savey = self.g_sy
            self.g_search_string = ''

            j = self.g_sy
            while j < len(self.g_buf):
                buf = self.g_buf[j]
                if buf.find(findstr) > -1:
                    self.g_sx = buf.find(findstr)
                    self.g_sy = j
                    self.show()
                    self.status()
                    self.g_search_string = findstr
                    break
                j += 1

            if j >= self.g_ny:
                self.status("Search wrapped to beginning of file.")

                for j in range(len(self.g_buf)):
                    if j >= self.g_sy:
                        break
                    buf = self.g_buf[j]
                    if buf.find(findstr) > -1:
                        self.g_sx = buf.find(findstr)
                        self.g_sy = j
                        self.show()
                        self.status()
                        self.g_search_string = findstr
                        break

            if savey == self.g_sy:
                self.status("Item '"+findstr+"' not found.")
            else:
                self.g_search_string = cmd


    def searchup(self, cmd):

        sp = cmd.split(' ')

        if len(sp) < 1:
            self.g_search_string = ''
            self.status('Search parameter not specified. Try again.')

        else:
            findstr = ""
            for j in range(len(sp)):
                #if j == 0: continue
                findstr += sp[j] + ' '

            if findstr[-1].isspace():
                findstr = findstr[:-1]

            savey = self.g_sy
            self.g_search_string = ''

            #for j in range(len(self.g_buf)):
            #    if j < self.g_sy: continue
            j = self.g_sy
            while j > -1:
                buf = self.g_buf[j]
                if buf.find(findstr) > -1:
                    self.g_sx = buf.find(findstr)
                    self.g_sy = j
                    self.show()
                    self.status()
                    self.g_search_string = findstr
                    break
                j -= 1

            if j < 0:
                self.status("Search wrapped to end of file.")

                j = self.g_ny-1
                while j > self.g_sy:
                    buf = self.g_buf[j]
                    if buf.find(findstr) > -1:
                        self.g_sx = buf.find(findstr)
                        self.g_sy = j
                        self.show()
                        self.status()
                        self.g_search_string = findstr
                        break
                    j -= 1

            if savey == self.g_sy:
                self.status("Item '"+findstr+"' not found.")
            else:
                self.g_search_string = cmd


    # return True if wintop changes ...
    #              F  y         L    n
    # -------------[------------]-----
    #
    def setwintop(self):

        F = self.wintop()
        L = self.winbot()
        Y = self.g_sy
        N = self.g_ny

        if F <= Y < L:
            ret = False
        elif Y < F:
            self.g_by = Y
            ret = True
        elif Y >= L:
            self.g_by = Y-self.g_cli_line+1
            ret = True
        return ret


    def show(self, line=-1):

        if self.g_ny > 0:
            if line < 0:
                self.refresh()
            else:
                blank = '\r'
                for j in range(self.g_nx):
                    blank += ' '
                blank += '\r'
                printr(blank)
                printr(self.g_buf[line])
        self.status()


    def status(self, text=''):

        if not self.g_nx:
            printr(self.esc_cursline.format(self.g_cli_line))
            printr("===\nStarting ...")
            return

        if self.setwintop():
            self.refresh()

        printr(self.esc_cursline.format(self.g_cli_line))
        for j in range(self.g_nx-1):
            printr(" ")

        Y = self.g_sy
        X = self.g_sx
        ch = self.charat(X, Y)

        print("\r>")
        if not len(text):

            printr("\rFile '{}' {} Lines".format(self.g_fn, len(self.g_buf)))

            if self.g_sx > self.g_nx:
                self.g_nx = self.g_sx

            if ch.isspace():
                ch = ' '

            cursxy = "{:3},{:3} [{}]".format(Y+1, X, ch)
            printr(self.esc_cursxpos.format(self.g_nx-len(cursxy)))
            printr(cursxy)

        else:

            for j in range(self.g_nx-1):
                printr(" ")

            printr("\r{}".format(text))


        if Y-self.g_by <= 0:
            #self.g_sy = 0
            printr(self.esc_curstop)
        else:
            printr(self.esc_cursline.format(Y-self.g_by))
        if X <= 0:
            printr('\r')
        else:
            printr(self.esc_cursxpos.format(X))



    def trim(self, txt):

        if len(txt) < 1:
            return txt

        try:
            while self.isspace(txt[-1]):
                txt = txt[:-1]

            while self.isspace(txt[0]):
                txt = txt[1:]

            s = ""
            for c in txt:
                s += c

        except:
            return txt

        return s


    def tostr(self, lst):
        s = ""
        for ln in lst:
            s += ln
        return s

    def yank(self):

        ch = self.getkey()

        if ch == self.YANK_LINE:
            self.g_yanked = ch
            self.yankline()
        elif ch == self.YANK_WORD:
            self.g_yanked = ch
            self.yankword()


    def yankline(self):
        self.g_yanked = 'y'
        self.g_yankline = self.g_buf[self.g_sy]


    def yankword(self):
        buf = str(self.g_buf[self.g_sy])
        for d in [' ', '\n', '\r', '\t']:
            sp = buf.split(d)
            if len(sp) > 0:
                break
        if len(sp) > 0:
            ln = ''
            for j in range(len(sp)):
                ln += sp[j]
                if len(ln) > self.g_sx:
                    self.g_yankword = sp[j]
                    break


    def wintop(self):
        return self.g_by


    def winbot(self):
        return self.g_by+self.g_cli_line


    def wrfile(self, fname, buf):

        with open(fname, 'w') as f:
            f.write(buf)
        #self.status("WrFile " + str(fname))


    def wrlines(self, fname, lst):

        s = self.tostr(lst)
        self.wrfile(fname, s)


    '''
    System methods
    '''
    def SysCAT(self, cmd):

        print('')
        cs = str(cmd).split(' ')
        if len(cs) > 1:
            self.SysHEAD(cmd, 1 << 30)
        else:
            self.status('cat requires 1 parameter: cat filename')


    def SysCD(self, cmd):

        print('')
        cs = str(cmd).split(' ')

        if len(cs) > 1:
            f1 = cs[1]

            try:
                os.chdir(f1)
            except:
                self.status('cd failed')

        else:
            self.status('cd requires 1 parameter: cd path')


    def SysCOPY(self, cmd):

        print('')
        cs = str(cmd).split(' ')

        if len(cs) > 2:
            f1 = cs[1]
            f2 = cs[2]

            if not self.pathexists('./'+f1):
                self.status('Cant find fromfile: '+f1)
                return
            if self.pathexists('./'+f2):
                self.status('"'+f2+'" exists; remove or rename before copy. ')
                return

            try:
                with open(f1,'r') as fromfile, open(f2,'w') as tofile:
                    while True:
                        ln = fromfile.readline()
                        if not ln:
                            break
                        tofile.write(ln)
            except:
                self.status('copy failed')
        else:
            self.status('copy requires 2 parameters: copy fromfile tofile')


    def SysDELETE(self, cmd):

        print('')
        cs = str(cmd).split(' ')
        if len(cs) > 1:
            fn = './'+cs[1]
            if self.pathexists(fn):
                os.remove(fn)
        else:
            self.status('delete requires 1 parameter: del filename')


    def SysHEAD(self, cmd, n=10):

        print('')
        cs = str(cmd).split(' ')

        if len(cs) > 2:
            lcnt = int(cs[2])
        else:
            lcnt = n

        if len(cs) > 1:
            f = cs[1]

            with open(f) as f:
                for i in range(lcnt):
                    l = f.readline()
                    if not l: break
                    sys.stdout.write(l)
        else:
            self.status('head requires at least 1 parameter: head filename [optional_length]')


    def SysLS(self, cmd):

        print('')
        cs = str(cmd).split(' ')
        if len(cs) > 1:
            path = cs[1]
        else:
            path = '.'

        print(" " + path + ": ")
        lst = []
        try:
            lst = os.listdir(path)
            lst.sort()
        except:
            path = './'+path
            if self.pathexists(path):
                lst = [path]

        for f in lst:
            st = os.stat("./%s" % (f))
            if st[0] & 0x4000:  # stat.S_IFDIR
                print("   <dir> %s" % f)
            else:
                print("% 8d %s" % (st[6], f))


    def SysMOVE(self, cmd):

        print('')
        cs = str(cmd).split(' ')

        if len(cs) > 2:
            f1 = cs[1]
            f2 = cs[2]

            try:
                os.rename(f1, f2)
            except:
                self.status('move failed')

        else:
            self.status('move requires 2 parameters: move fromfile tofile')

    def SysMKDIR(self, cmd):

        print('')
        cs = str(cmd).split(' ')

        if len(cs) > 1:
            f1 = cs[1]

            try:
                os.mkdir(f1)
            except:
                self.status('mkdir failed')

        else:
            self.status('mkdir requires 1 parameter: mkdir path')


    def SysPWD(self):

        print('')
        print(os.getcwd())


    def SysRMDIR(self, cmd):

        print('')
        cs = str(cmd).split(' ')

        if len(cs) > 1:
            f1 = cs[1]

            try:
                os.rmdir(f1)
            except:
                self.status('rmdir failed')

        else:
            self.status('rmdir requires 1 parameter: rmdir path')


    '''
    shell command handler
    '''
    def doShCommand(self, cmd):

        # print("Shell Command "+str(cmd))
        cmd = self.trim(cmd)
        cmd = cmd.lower()

        # print("CMD "+str(cmd))
        if cmd.find("ls") > -1:
            self.SysLS(cmd)

        if cmd == "clear":
            self.clear()

        if cmd == "cls":
            self.clear()

        if cmd == "pwd":
            self.SysPWD()

        if cmd.find("cat") > -1:
            self.SysCAT(cmd)

        if cmd.find("copy") > -1:
            self.SysCOPY(cmd)

        if cmd.find("cp") > -1:
            self.SysCOPY(cmd)

        if cmd.find("del") > -1:
            self.SysDELETE(cmd)

        if cmd.find("head") > -1:
            self.SysHEAD(cmd)

        if cmd.find("mkdir") > -1:
            self.SysMKDIR(cmd)

        if cmd.find("mv") > -1:
            self.SysMOVE(cmd)

        if cmd.find("rename") > -1:
            self.SysMOVE(cmd)

        if cmd.find("rm") > -1:
            self.SysDELETE(cmd)

        if cmd.find("rmdir") > -1:
            self.SysRMDIR(cmd)


        input("\nPress ENTER to continue...")
        self.show()



    '''
    Editor commands handler
    '''
    def doEdCommand(self, cmd):

        retcode = True
        puthist = True
        if self.g_command_replay:
            puthist = False

        hist = self.hist_prep()

        key = ''
        try:
            key = cmd[0]
        except:
            pass

        if not key or key == '':
            pass

        elif self.isnumeric(key):
            if key == '0' and self.g_nums == '':
                self.g_sx = 0
                self.status()
            else:
                self.g_nums += key

        elif key == 'r':
            line = self.g_sy
            buf = self.g_buf[line]
            if buf == '\n':
                buf = ' \n'
            ch = self.getkey()
            index = self.g_sx
            lb1 = buf[:index]
            lb2 = buf[index+1:]
            buf = lb1 + ch + lb2
            printr('\r'+buf)
            self.g_buf.pop(line)
            self.g_buf.insert(line, buf)
            self.status()

        elif key == 'R':
            line = self.g_sy
            if self.g_buf[line] == '\n':
                self.g_buf[line] = ' \n'
            lst = [c for c in self.g_buf[line]]
            while self.g_sx < len(lst)-1:
                ch = self.getkey()
                try:
                    esc = ord(ch)
                except:
                    pass
                if not esc or esc == self.CTL_ESC:
                    break
                else:
                    lst[self.g_sx] = ch
                    printr(ch)
                    self.g_sx += 1
                    #self.status() don't need it for 'R'
            buf = ''
            for ch in lst:
                buf += ch
            self.g_buf.pop(line)
            self.g_buf.insert(line, buf)
            self.status()

        elif key == 's':
            self.deletechar()
            self.insertchars(self.g_sx)

        elif key == 'x':
            self.deletechar()

        elif key == 'a':
            self.appendchars(self.g_sx)

        elif key == 'A':
            ln = self.g_buf[self.g_sy]
            cnt = len(ln) - 2  # append adds 1 to index sub '\n' too
            self.appendchars(cnt)

        elif key == 'c':

            ch = self.getkey()

            if ch == 'w': # change to end of word
                self.deleteword(1)
                self.insertchars(self.g_sx)
            elif ch == 'e': # same as w
                self.deleteword(1)
                self.insertchars(self.g_sx)
            elif ch == 'c': # broken TBD fix
                self.deleteline(1)
                self.insertline(1)

            '''
            elif ch == 'i','w' # change entire word
            elif ch == '$' # change to end of line
            '''

        # ???
        elif key == 'c':
            ch = self.getkey()

            if ch == 'w':
                self.gotowordbegin()
                self.deleteword(1)
                self.insertchars(0)
            elif ch == 'e':
                self.deleteword(1)
                self.insertchars(0)
            elif ch == '$':
                self.deleteline(1)
                self.insertline(1)

        elif key == 'D':
            self.deletelinetoend()

        elif key == 'd':

            nums = ''
            dnum = 1
            #icmd = ""
            try:

                j = 1
                while True:
                    ch = self.getkey()
                    if ch == 'd':
                        if j > 1:
                            dnum = int(nums)
                        self.deleteline(dnum)
                        break
                    elif ch == 'w':
                        if j > 1:
                            dnum = int(nums)
                        self.deleteword(dnum)
                        break
                    elif self.isnumeric(ch):
                        j += 1
                        nums += ch
                    else:
                        self.status("Unknown command: {}".format(cmd))
                        break

                self.show()

            except:
                # don't bomb
                pass

        elif key == 'G':
            if self.g_nums != '':
                # g_nums is only > 0 as '0' is a command
                self.g_sy = int(self.g_nums)-1
                self.g_nums = ''
            else:
                self.g_sy = self.g_ny-1
            self.show()

        elif key == 'i':
            self.insertchars(self.g_sx)

        elif key == 'I':
            self.insertchars(0)

        elif key == 'J':
            self.joinlines()

        elif key == 'o':
            self.insertline(1)

        elif key == 'O':
            self.insertline(0)

        elif key == 'p':
            if self.g_yanked == 'w':
                self.pasteword(1)
            else:
                self.pasteline(1)

        elif key == 'P':
            if self.g_yanked == 'w':
                self.pasteword(0)
            else:
                self.pasteline(0)

        elif key == 'y':
            self.yank()

        elif key == 'Z':
            ch = self.getkey()
            if ch == 'Z':
                try:

                    if len(self.g_fn) == 0:
                        print("No file name.")
                        return

                    self.wrlines(self.g_fn, self.g_buf)
                    sys.exit()

                except:
                    # don't bomb
                    pass

        else:
            print("Unknown command '{}'".format(key))
            retcode = False

        if puthist:
            self.hist_push(hist)

        return retcode


    def doCommand(self, key):

        retcode = True

        if key == ':':
            self.bottom()
            printr('\r')
            for j in range(self.g_nx):
                printr(' ')
            printr('\r'+key)

            cmd = self.getCommand()

            if cmd[0] == '!':
                self.doShCommand(cmd[1:])

            elif cmd[0] == 'e':

                file = self.trim(cmd[1:])

                if not self.pathexists(file):
                    self.status("No such file: "+file)

                else:
                    try:
                        self.g_fn = file
                        self.g_buf = self.rdfile(self.g_fn)
                        self.g_sx = 0
                        self.g_sy = 0
                        self.g_nx = 0
                        self.g_by = 0
                        self.g_ny = len(self.g_buf)
                        self.show()

                    except OSError as err:
                        # don't bomb
                        self.status("Exception {} {}".format(self.g_fn, err))

            elif cmd[0] == 'w':

                try:
                    file = self.trim(cmd[1:])
                    #file = str(cmd).split(' ')
                    if len(file) > 1:
                        self.g_fn = file

                    if len(self.g_fn) == 0:
                        print("No file name.")
                        return

                    try:
                        self.wrlines(self.g_fn, self.g_buf)
                        self.status("Saved '{}' {} lines.".format(self.g_fn,self.g_ny))

                    except OSError as err:
                        # don't bomb
                        self.status("Exception {} {}".format(self.g_fn, err))

                except:
                    # don't bomb
                    pass


            elif cmd[0] == 'q':
                # quit() will not work in upython
                # sys.exit() works with any environment
                sys.exit()


            elif self.isnumeric(cmd[0]):
                # simple goto for now ... split later
                num = int(cmd)
                if num > 0:
                    num -= 1
                if num < self.g_ny:
                    self.g_sy = num
                else:
                    self.g_sy = self.g_ny - 1
                self.show()

            #else: # why this ?
            #    self.doEdCommand(cmd[0:])

        elif key == '/':

            self.g_search_dir = 1
            self.bottom()
            printr('\r')
            for j in range(self.g_nx):
                printr(' ')
            printr('\r'+key)

            cmd = self.getCommand()

            self.searchdown(cmd)

        elif key == '?':

            self.g_search_dir = -1
            self.bottom()
            printr('\r')
            for j in range(self.g_nx):
                printr(' ')
            printr('\r'+key)

            cmd = self.getCommand()

            self.searchup(cmd)

        elif key == '.':
            self.hist_repeat()

        elif key == 'u':
            self.hist_undo()

        elif key == 'U':
            self.hist_redo()

        elif key == 'n':

            if not len(self.g_search_string):
                self.status('No previous search.')

            else:
                cmd = self.g_search_string

                self.bottom()
                printr('\r')
                for j in range(self.g_nx):
                    printr(' ')
                printr('\r' + key)

                if self.g_search_dir > 0:
                    if self.g_sy < self.g_ny:
                        self.g_sy += 1
                    self.searchdown(cmd)
                else:
                    if self.g_sy > 0:
                        self.g_sy -= 1

                    self.searchup(cmd)

        else:
            retcode = False

        if retcode:
            self.g_last_cmd = ''

        return retcode


    def navigate(self, key):

        retcode = True

        if key == '0':
            self.g_sx = 0
            self.status()

        elif key == '$':
            if self.g_sy < self.g_ny:
                ln = self.g_buf[self.g_sy]
                cnt = len(ln)-1
                self.g_sx = cnt
                self.status()

        elif key == 'b':
            self.gotowordbegin()

        elif key == 'e':
            self.gotowordend()

        elif key == 'w':
            self.gotowordnext()

        elif key == 'h':
            if self.g_sx > 0:
                self.g_sx -= 1
            self.status()

        elif key == 'j':
            if self.g_sy < self.g_ny-1:
                self.g_sy += 1
            if self.g_ny > 1:
                # len()-1 since each line has a '\n'
                llen = len(self.g_buf[self.g_sy])-1
                if llen < self.g_sx:
                    self.g_sx = llen-1 # array is 0 based
                self.status()

        elif key == 'k':
            if self.g_sy > 0:
                self.g_sy -= 1
                # this doesn't really look right, but without, it bombs
                if self.g_sy > 0:
                    llen = len(self.g_buf[self.g_sy])-1
                else:
                    llen = len(self.g_buf[self.g_sy])
                if llen < self.g_sx:
                    self.g_sx = llen-1 # array is 0 based
                self.status()

        elif key == 'l':
            llen = 0
            if len(self.g_buf) > 0:
                llen = len(self.g_buf[self.g_sy])
            if self.g_sx < llen:
                # len()-2 since each line has a '\n'
                # and we don't want to be past the char
                llen = len(self.g_buf[self.g_sy]) - 2
                if self.g_sx < llen:
                    self.g_sx += 1
            self.status()

        else:
            retcode = False

        if retcode:
            self.g_last_cmd = ''

        return retcode


    def errorbytes(self, msg=''):
        print("Byte Error: "+str(msg))


    def getCommand(self):

        cmd = []
        while True:
            ch = self.getkey()
            # for now just clobber \t - TBD handle better later
            if ch == '\t':
                ch = ' '
            if ch == '\b':
                cmd = cmd[:-1]
            else:
                cmd.append(ch)
            printr(ch)
            if ch == '\n' or ch == '\r':
                cmd = self.tostr(self.trim(cmd))
                break

        return cmd


    def getescaped(self, key):

        if key == 'H':   # arrow up
            return 'k'
        elif key == 'K': # arrow left
            return 'h'
        elif key == 'M': # arrow right
            return 'l'
        elif key == 'P': # arrow down
            return 'j'
        elif key == 'G': # go to beg of line
            self.g_sx = 0
            self.status()
            return '\r'
        elif key == 'O': # go to end of line
            pos = len(self.g_buf[self.g_sy])
            self.g_sx = pos
            self.status()
            return '\r'
        elif key == 'I': # page down
            page = self.g_sy - self.g_cli_line
            if page >= 0:
                self.g_sy = page
                self.status()
            return '\r'
        elif key == 'Q': # page down
            page = self.g_sy + self.g_cli_line
            if page <= self.g_ny:
                self.g_sy = page
                self.status()
            return '\r'
        elif key == 'R':
            if self.g_cmd:
                return 'R'
            else:
                return '\33'
        elif key == 'S':
            if self.g_cmd:
                return 'x'
            else:
                return '\33'

        raise("No Escape! Haha! "+key)


    '''
    sometimes we need a buffered string because of \b etc...
    '''
    def getstring(self):
        s = ''
        while True:
            ch = self.getch()
            if ch == '\n' or ch =='\r':
                break
            if ch == '\b':
                s = s[:-1]
            if ch == '\t':
                ch = ' '
                s += ch
            if self.isalnumeric(ch):
                s += ch
        return s


    def getkey(self):

        if self.g_command_replay > 0:
            if self.g_command_replay < len(self.g_last_cmd):
                key = self.g_last_cmd[self.g_command_replay]
                self.g_command_replay += 1
            else:
                key = ''

            return key

        #if os.name == 'nt':
        try:
            # windows? version
            import msvcrt
            while True:
                key = msvcrt.getch()
                if not ord(key):
                    msvcrt.getch()
                if key == '\b':
                    continue
                break

        except:
            # micropython version
            import usys
            while True:
                key = usys.stdin.read(1)
                #printr('{}'.format(key))
                if key == '\b':
                    continue
                break

        try:

            if ord(key) == 0xE0:
                key = self.getkey()
                key = self.getescaped(key)

            elif ord(key) == 0:
                key = self.CTL_ESC
                self.g_command_start = False

            elif ord(key) == self.CTL_ESC:
                key = self.CTL_ESC
                self.g_command_start = False

            else:
                key = key.decode('utf-8')


        except:
            # don't bomb ...
            # usys.stdin.read returns a char
            # and not a bytes buffer.
            pass

        #if not self.g_command_replay:
        if self.isalnumeric(key):
            self.g_last_cmd += key
        elif self.keyval(key) == self.CTL_ESC:
            return self.CTL_ESC

        return key


    def hist_prep(self):

        hist = edhist()
        hist.x = self.g_sx
        hist.y = self.g_sy
        return hist


    def hist_push(self, hist):

        #hist = edhist()
        hist.cmd = self.g_cmd_key
        #hist.x = self.g_sx
        #hist.y = self.g_sy
        hist.nx = self.g_nx
        hist.ny = self.g_ny
        hist.last_cmd = self.g_last_cmd
        self.g_history.append(hist)
        self.g_command_start = False
        self.g_command_replay = 0
        self.g_last_cmd = ''
        self.g_history_ndx += 1


    def hist_repeat(self):

        if len(self.g_history) < 1:
            self.status("No history to repeat.")
        else:
            hist = self.g_history[-1]
            hist.x = self.g_sx
            hist.y = self.g_sy
            self.g_last_cmd = hist.last_cmd
            self.g_command_replay = 1
            self.doEdCommand(self.g_last_cmd[0])
            self.g_command_replay = 0
            #self.hist_push(hist)


    '''
    How to redo/undo history?
        Use virgin rebuild strategy.
        Reset read file to virgin g_bufnew (:e file or startup)
        Create g_buf from virgin g_bufnew
        Save new edit commands
        Undo replay stored history commands against virgin g_bufnew
        Redo is just a special case of undo that adds history
    '''
    def hist_redo(self):

        hlen = len(self.g_history)

        if self.g_history_ndx < hlen:
            self.g_history_ndx += 1
            self.hist_undo(0)
        else:
            self.status("No more history to redo.")

    def hist_undo(self, pos=-1):

        hlen = len(self.g_history)
        if hlen < 1:
            self.status("History not made.")

        elif self.g_history_ndx < 1:
            self.status("No more history.")

        else:
            self.g_buf.clear()
            for item in self.g_bufnew:
                self.g_buf.append(item)
            self.g_sx = 0
            self.g_sy = 0
            self.g_nx = 0
            self.g_by = 0
            self.g_ny = len(self.g_buf)

            # need local copy as command changes ndx
            count = self.g_history_ndx + pos

            j = 0
            self.g_command_replay = 1
            while j < count:
                hist = self.g_history[j]
                self.g_sx = hist.x
                self.g_sy = hist.y
                self.g_last_cmd = hist.last_cmd
                self.g_command_replay = 1
                self.doEdCommand(self.g_last_cmd[0])
                #self.refresh()
                j += 1

            self.g_command_replay = 0
            self.g_history_ndx = count
            self.refresh()


    def keyval(self, key):
        try:
            val = ord(key)
        except:
            val = key
        return val


    def run(self, file=''):

        self.clear()

        if len(file) > 0:
            self.g_fn = file
            self.g_buf = self.rdfile(self.g_fn)
            for item in self.g_buf:
                self.g_bufnew.append(item)

            self.g_sy = 0
            lines = len(self.g_buf)
            self.g_ny = lines
            if self.g_ny > 0:
                self.refresh()
            self.status()

        else:
            self.g_buf.insert(0, "Hello, world.\n")
            self.g_sy = 0
            self.g_sx = 0
            self.g_ny = 1
            self.g_nx = 40
            self.refresh()
            self.status()

        while True:

            key = self.getkey()

            if key == 0 or key == '' or key == '\n' or key == '\r':
                continue

            elif self.keyval(key) == self.CTL_ESC:
                self.g_cmd = True
                continue

            elif self.keyval(key) == self.CTL_C:
                break

            elif self.keyval(key) == self.CTL_G:
                self.status()

            elif self.keyval(key) == self.CTL_L:
                self.refresh()

            elif self.keyval(key) == self.CTL_R:
                self.hist_redo()

            elif self.keyval(key) == self.CTL_D or self.keyval(key) == self.CTL_F:
                newline = self.g_sy + self.g_cli_line * 2
                if newline < self.g_ny:
                    self.g_sy = newline
                self.status()
                newline = self.g_sy - self.g_cli_line
                if newline < self.g_ny:
                    self.g_sy = newline
                self.status()

            elif self.keyval(key) == self.CTL_B or self.keyval(key) == self.CTL_P:
                newline = self.g_sy - self.g_cli_line
                if newline >= 0:
                    self.g_sy = newline
                self.show()
                self.status()

            elif self.keyval(key) > 127:
                key = self.getkey()

            elif self.navigate(key):
                pass

            elif self.doCommand(key):
                pass

            else:
                self.g_command_start = True
                self.g_cmd_key = key
                self.g_last_cmd = key
                self.doEdCommand(key)


if __name__ == "__main__":

    e = editor()
    if len(sys.argv) > 1:
        e.run(sys.argv[1])
    else:
        e.run()
