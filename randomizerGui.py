from tkinter import *
from tkinter import ttk, filedialog

from randomizeGame import *
from sgzGame import RandomizerFlags

def open_rom():
    romPath = filedialog.askopenfilename(
        initialdir = "./",
        title = "Select Super Godzilla US v1.1 Location"
    )

    openRomLabel['state'] = NORMAL
    openRomLabel.delete('1.0', END)
    openRomLabel.insert('1.0', romPath)
    openRomLabel['state'] = DISABLED

def patch_rom():
    timeValue = int(timeLimitField.get())
    if timeValue < 0:
        timeValue = 0
    elif timeValue > 999:
        timeValue = 999

    randomizerFlags = RandomizerFlags(
        timeValue,
        randomMaps.get(),
        persistentEnergy.get(),
        persistentTime.get(),
        True, # Logic Critical Tiles
        True, # Logic General Event Tiles
        True, # MGZ Warp Disable
        noStartingContinues.get(),
        noAddedContinues.get()
    )

    print(f'romPath.get():{openRomLabel.get("1.0", END)}')
    romPath = openRomLabel.get("1.0", END).strip()
    randomize_game(romPath, randomizerFlags)
    window.destroy()


window = Tk()
window.option_add('*Font', '32')

defaultTimeLimit = 768

randomMaps = BooleanVar()
persistentTime = BooleanVar()
persistentEnergy = BooleanVar()
noStartingContinues = BooleanVar()
noAddedContinues = BooleanVar()
filename = StringVar()

# Default to standard options
randomMaps.set(True)
persistentTime.set(True)
persistentEnergy.set(True)
noStartingContinues.set(True)
noAddedContinues.set(True)

openRomButton = Button(window, text="Select Rom (Only US Version 1.1 Currently Supported)", command=open_rom)
openRomButton.place(x=32, y=32)

openRomLabel = Text(window, height=1, width=76, state='disabled')
openRomLabel.place(x=32, y=64)

timeLimitLabel = Label(window, text="Time Limit:")
timeLimitLabel.place(x=40, y=100)

timeLimitField = Entry(window, width=5) #state='disabled')
timeLimitField.place(x=128, y=96)
timeLimitField.insert(0, defaultTimeLimit)

ptCheck = Checkbutton(window, text='Persistent Time', variable=persistentTime)
ptCheck.place(x=32, y=128)

peCheck = Checkbutton(window, text='Persistent Energy', variable=persistentEnergy)
peCheck.place(x=32, y=160)

nscCheck = Checkbutton(window, text='No Starting Continues', variable=noStartingContinues)
nscCheck.place(x=32, y=192)

nacCheck = Checkbutton(window, text='No Added Continues', variable=noAddedContinues)
nacCheck.place(x=32, y=224)

randomMapsCheck = Checkbutton(window, text='Randomize Maps', variable=randomMaps)
randomMapsCheck.place(x=32, y=256)

patchButton = Button(window, text="Patch Rom!", command = patch_rom)
patchButton.place(x=32, y=320)


window.title('Super Godzilla Randomizer')
window.geometry('768x384+16+16')

window.mainloop()

