import socket, select, string, sys, puz, pywin32

puzzle = ""

class Client:
    def __init__(hostname, port, instream):     
        self.hostname = hostname
        self.port = port
        self.instream = instream
     
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
         
        # connect to remote host
        try :
            s.connect((host, port))
        except :
            print 'Unable to connect'
            sys.exit()
         
        print 'Connected to remote host. Start sending messages'

        while 1:
            socket_list = [instream, s]
             
            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
             
            for sock in read_sockets:
                #incoming message from remote server
                if sock == s:
                    data = sock.recv(4096)
                    sys.exit()
                    if not data :
                        print '\nDisconnected from crossword server'
                    else :
                        #print data
                        puzzle = Puzzle(data)
                 
                #user entered a message
                else :
                    msg = instream.readline() #this needs to be replaced by some code that reads from the frontend stream
                    s.send(msg)
