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
    randomizerFlags = RandomizerFlags(
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

window = Tk()
window.option_add('*Font', '32')

#romPath = StringVar()

persistentTime = BooleanVar()
persistentEnergy = BooleanVar()
noStartingContinues = BooleanVar()
noAddedContinues = BooleanVar()
filename = StringVar()

openRomButton = Button(window, text="Select Rom (Only US Version 1.1 Currently Supported)", command=open_rom)
openRomButton.place(x=32, y=32)

openRomLabel = Text(window, height=1, width=64, state='disabled')
openRomLabel.place(x=32, y=72)

ptCheck = Checkbutton(window, text='Persistent Time', variable=persistentTime)
ptCheck.place(x=32, y=128)

peCheck = Checkbutton(window, text='Persistent Energy', variable=persistentEnergy)
peCheck.place(x=32, y=160)

nscCheck = Checkbutton(window, text='No Starting Continues', variable=noStartingContinues)
nscCheck.place(x=32, y=192)

nacCheck = Checkbutton(window, text='No Added Continues', variable=noAddedContinues)
nacCheck.place(x=32, y=224)

patchButton = Button(window, text="Patch Rom!", command = patch_rom)
patchButton.place(x=32, y=256)

window.title('Super Godzilla: Final Weapon')
window.geometry('768x384+16+16')

window.mainloop()

