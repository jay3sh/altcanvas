

class PathContext:
    cpx = 0.0
    cpy = 0.0
    rpx = 0.0
    rpy = 0.0
    cmd = None
    param = 0 
    rel = None
    params = [0,0,0,0,0,0,0]



def parse_path(path_data):

    ctx = PathContext()

    val = 0.0
    in_num = False
    in_frac = False
    in_exp = False
    exp_wait_sign = False
    sign = 0
    exp = 0
    exp_sign = 0
    frac = 0.0

    for c in path_data:
        if c >= '0' and c <= '9':
            # Digit
            if in_num:
                if in_exp:
                    exp = (exp * 10) + ord(c) - ord('0')
                    exp_wait_sign = False
                elif in_frac:
                    frac *= 0.1
                    val += frac * (ord(c) - ord('0'))
                else:
                    val = (val * 10) + (ord(c) - ord('0'))
            else:
                in_num = False
                in_frac = False
                in_exp = False
                exp = 0
                exp_sign = 1
                exp_wait_sign = False
                val = ord(c) - ord('0')
                sign = 1

        elif c == '.':
            if not in_num:
                in_num = True
                val = 0
            in_frac = True
            frac = 1
        elif (c == 'E' or c == 'e') and in_num:
            in_exp = True
            exp_wait_sign = True
            exp = 0
            exp_sign = 1
        elif (c == '+' or c == '-') and in_exp:
            if c == '+':
                exp_sign = 1
            else:
                exp_sign = -1
        elif in_num:
            val *= sign * pow(10, exp_sign * exp)
            if ctx.rel:
                if ctx.cmd in ('l', 'm', 'c', 's', 'q', 't'):
                    if (ctx.param & 1 == 0):
                        val += ctx.cpx
                    elif (ctx.param & 1 == 1):
                        val += ctx.cpy

                elif ctx.cmd is 'a':
                    if ctx.param == 5:
                        val += ctx.cpx
                    elif ctx.param == 6:
                        val += ctx.cpy

                elif ctx.cmd is 'h':
                    val += ctx.cpx

                elif ctx.cmd is 'v':
                    val += ctx.cpy

            ctx.params[ctx.param] = val
            ctx.param += 1

            do_cmd(ctx, False)

            in_num = False

        if c == '\0':
            break

        elif (c == '+' or c == '-') and not exp_wait_sign:
            if c == '+':
                sign = 1
            else:
                sign = -1

            val = 0
            in_num = True
            in_frac = False
            in_exp = False
            exp = 0
            exp_sign = 1
            exp_wait_sign = False

        elif c == 'z' or c == 'Z':
            if ctx.param > 0:  # TODO check
                do_cmd(ctx, True)
                pass

            #TODO close_path

            #TODO
            ctx.cpx = ctx.rpx 
            ctx.cpy = ctx.rpy
        elif (c >= 'A' and c <= 'Z' and c is not 'E'):
            if ctx.param > 0:
                do_cmd(ctx, True)
                pass

            ctx.cmd = chr(ord(c) + ord('a') - ord('A'))
            ctx.rel = False
        elif (c >= 'a' and c <= 'z' and c is not 'e'):
            if ctx.param > 0:
                do_cmd(ctx, True)
                pass
            ctx.cmd = c
            ctx.rel = True
        # else c should be whitespace or , 



def do_cmd(ctx, final):
    if ctx.cmd is 'm':
        if ctx.param == 2 or final:
            print 'moveto %d %d'%(ctx.params[0], ctx.params[1])
            ctx.cpx = ctx.rpx = ctx.params[0]
            ctx.cpy = ctx.rpy = ctx.params[1]
            ctx.param = 0

    elif ctx.cmd is 'l':
        if ctx.param == 2 or final:
            print 'lineto %d %d'%(ctx.params[0], ctx.params[1])
            ctx.cpx = ctx.rpx = ctx.params[0]
            ctx.cpy = ctx.rpy = ctx.params[1]
            ctx.param = 0

    elif ctx.cmd is 'c':
        if ctx.param == 6 or final:
            x1, y1, x2, y2, x3, y3 = ctx.params[0:6]
            print 'curve to %d %d %d %d %d %d'%(x1, y1, x2, y2, x3, y3)
            ctx.rpx = x2
            ctx.rpy = y2
            ctx.cpx = x3
            ctx.cpy = y3
            ctx.param = 0
    elif ctx.cmd is 's':
        print 'Not implemented '+ctx.cmd
    elif ctx.cmd is 'h':
        print 'Not implemented '+ctx.cmd
    elif ctx.cmd is 'v':
        print 'Not implemented '+ctx.cmd
    elif ctx.cmd is 'q':
        print 'Not implemented '+ctx.cmd
    elif ctx.cmd is 't':
        print 'Not implemented '+ctx.cmd
    elif ctx.cmd is 'a':
        print 'Not implemented '+ctx.cmd
    else:
        print 'default'
        ctx.param = 0
                
            

if __name__ == '__main__':
    path='M205.65,98.19c0,0-1.429,3.75-3.215,5.894     c-1.786,2.143-6.429,3.572-11.608,3.215c-5.18-0.357-9.645-6.43-10.717-9.645C191.004,99.976,199.22,99.976,205.65,98.19z      M179.039,91.403l-4.644,3.394c0,0,0,4.108,3.572,9.108c3.572,5.001,9.287,8.751,14.824,8.395     c5.536-0.357,12.859-4.287,14.466-6.787c1.608-2.5,4.822-10.716,4.822-10.716l-3.929-3.214c-5.715,2.679-12.859,2.5-16.431,2.5     S182.789,93.725,179.039,91.403z'
    parse_path(path)
        

