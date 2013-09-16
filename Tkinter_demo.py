from Tkinter import *
from tkFileDialog import askopenfilename

def txtfr(frame):
	
	#define a new frame and put a text area in it
	textfr=Frame(frame)
	text=Text(textfr,height=10,width=50,background='white')
	
	filename = askopenfilename(filetypes=[("allfiles","*"),("pythonfiles","*.py")])
	f=open(filename)
	lines=f.readlines()
	for line in lines:
		text.insert(END, line.strip() )
		text.insert(END, "\n")

	# put a scroll bar in the frame
	scroll=Scrollbar(textfr)
	text.configure(yscrollcommand=scroll.set)

	#pack it
	text.pack(side=LEFT)
	scroll.pack(side=RIGHT,fill=Y)
	textfr.pack(side=TOP)
	return

root = Tk()
frame = Frame(root)
frame.pack()

bottomframe = Frame(root)
bottomframe.pack( side = BOTTOM )

greenbutton = Button(frame, text="Green", fg="green")
greenbutton.pack( side = BOTTOM)

brownbutton = Button(frame, text="Brown", fg="brown")
brownbutton.pack( side = BOTTOM )

blbutton = Button(frame, text="Black", fg="black")
blbutton.pack( side = BOTTOM )

txtfr(frame)

root.mainloop()