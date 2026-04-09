import PySimpleGUI as sg
import subprocess
import platform
import os
from PIL import ImageColor
import matplotlib.font_manager as fm
import threading
import shutil
import signal
from packagefiles.edit_video import auto_game_montage
import multiprocessing

run_next_thread = False
base64_image = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAAIGNIUk0AAHomAACAhAAA+gAAAIDoAAB1MAAA6mAAADqYAAAXcJy6UTwAAAH+UExURQAAAP87If87If87If87If87If87If87If87If87If87ISUjJFAlIe5sFiUjJCMgIfU5IP87If46IPI5IKszH7lxFf93Fv90Fv9xF+pbGsMzINQ2IaovH62jC//xANnNBZGID6yKEfmAE/d4FL9JG9s2IKaRDvPOA+/FBX5UF89EHe04IF9YFf/wAPjeAe/DBL2VENA/Iek6IH9bFv7wAPvlAcKeC7Z1Eug5IKNlFO3gAv7xAPniAfDTA8N6EYstIMyUDuvdAvPNBJF7EfZcGeE3IPmQEfnsAP7oAfjWAvC3B/C1B/CzCIYrIP49IP63Cv+7Cf++Cf/BCNjMBfvoAO/CBdWkCfxBH6EvH6+lC/faAr6bC/CJELkyIP9IL/5zFsi2B/zpAPTRA+m3C7tQKHVTT/7sAPDFBGtZFftJHvw8I/k6IIpCG9WtCHwtH5k7HczABvzsAO7CBYNsE+BYGbIxILUxIOc4IP6UEcq+B/3tAPjfAvjeAtzHBaOZDZZ7EIpDG/5AH+5IJFk/KzYyHaCWDfrjAfHKA3dEGtw/H+o4IU9JGP3sAOK7BquCENc1IO44IIpYGfvnAfnhAc6RDXEvHn9CHOLVBPTUA6yTDfVzFMw0IGknIOPRBPDJBFw8GuVBHtVaGcilCcKQDMEzIPlnGMGLDYU8HMYzIP///xk1TTUAAAARdFJOUwAMWp+/Hg+PLc/vBoP2ARovY7xO3wAAAAFiS0dEqScPBgQAAAAHdElNRQfnCw0WKRQEGPwCAAABjklEQVQ4y2NggANGJmYWQSBgYWZiZMAErMyCSICZFU2ajV0QDbCzIctzcApiAE4OJHkuuLCQMJzJxYFFXlBEVExcQlJKGlkFG5L5MrJyQCCvoKikrAK0BeIOJPepqslBgLqGphbIpWD/IeS1dUCSunJ6+gaGELeAfIvwv5ExSN7E1MzcAh4ewPBDGGBpJSdnbWNrZ4/kWUYGJjjbwREo7+Ts4oocGkwIG9xMwBa4e3h6efv4IuxggbL8/AMCg4JBSkJCw8LhJrAwIJsXEQlUEBUdE4skBlYQB2HHJ8jJJSYlp6BECZIJqWlAV6RnZGZhV5CdYy1nHZWbhx6pcEfmF8hZFxYVl5SWlSPLs8C8WVEJDISq6prauvoGZAXMsIBqbGpuabWWk2tr7+hEDSh4UHd1y8n19Pb1ozqBER5ZEybqTpo8ZSqaE5kR0T1t+oyZs2aj+4EVnmDmzJ03fwG6NCTBgJPcwkWLl2BIw5IcMNEuXbYcUxqRrLl5eFfgk2fg4xcgkHEIZz3CmRd39gcA0k9l8LbQyIEAAAAldEVYdGRhdGU6Y3JlYXRlADIwMjMtMTEtMTNUMjI6NDE6MjArMDA6MDC1A2E6AAAAJXRFWHRkYXRlOm1vZGlmeQAyMDIzLTExLTEzVDIyOjQxOjIwKzAwOjAwxF7ZhgAAACh0RVh0ZGF0ZTp0aW1lc3RhbXAAMjAyMy0xMS0xM1QyMjo0MToyMCswMDowMJNL+FkAAAAASUVORK5CYII='
already_occured = False

if __name__ == '__main__':
    # Pyinstaller fix because ultralytics references differently
    multiprocessing.freeze_support()


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def retrieve_default_music():
    file_names = [f for f in os.listdir('default_audio') if os.path.isfile(os.path.join('default_audio', f))]
    file_names.extend(['other', 'none'])
    return file_names


def retrieve_available_fonts():
    system_fonts = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    font_names = [os.path.splitext(os.path.basename(font))[0] for font in system_fonts]
    return font_names


def retrieve_available_colors():
    available_colors = list(ImageColor.colormap.keys())
    return available_colors


sg.theme('Black')
dropdown_options4 = [("center"), ("center", "top"), ("center", "bottom"), ("left", "top"), ("right", "top"),
                     ("left", "bottom"), ("right", "bottom")]
dropdown_options = ["tiny", "base", "small", "medium", "large"]
dropdown_games = ["Fortnite", "MW 2019", "MWII 2022", "MWIII 2023", "Apex Legends",
                  "Rainbow Six Siege", "PUBG Mobile", "PUBG PC", "Destiny 2", "Rocket League", "CSGO", "Valorant", "Overwatch",
                  "Minecraft (PVP server)"]
# Define the layout of the GUI
auto_montage_layout = [
    [sg.Text("Which game is this?"),
     sg.Drop(values=dropdown_games, background_color='white', key="which_game", default_value="Fortnite",
             readonly=True, text_color='black',
             tooltip="Choose the game that your video contains.")],
    [sg.Text("Choose montage music"),
     sg.Drop(values=retrieve_default_music(), background_color='white', key="dropdown_audio",
             default_value="Shadows - Anno Domini Beats.mp3",
             readonly=True, text_color='black', size=30,
             tooltip="Choose the audio you want to overlay over your montage"),
     sg.FileBrowse(file_types=(("Audio Files", "*.mp3;*.wav;*.flac;*.ogg"),), visible=False,
                   key='music_choice', tooltip="Supported file types include: *.mp3;*.wav;*.flac;*.ogg")],
    [sg.Text("Edit with video effects:"),
     sg.Drop(values=["yes", "no"], background_color='white', key="effects_bool", default_value="yes",
             readonly=True, text_color='black',
             tooltip="This is selecting if you want video effects in the video or just the highlights, letting you edit yourself.")],
    [sg.Text("Adjust Music Volume (%):",
             tooltip="Volume of the overlayed music from 0-200%"),
     sg.Button("-", size=(1, 1), key='-VOL-', button_color=('white', 'darkred')),
     sg.Slider(range=(0, 200), default_value=100, orientation='h', size=(23, 10), trough_color="white",
               border_width=6,
               resolution=1,
               key='music_volume', tooltip="Volume of the overlayed music from 0-200%"),
     sg.Button("+", size=(1, 1), key='-VOL+', button_color=('white', 'darkgreen'))],
    [sg.Text("Make editing faster (frames):\n(forfit precision for speed)",
             tooltip="You can increase model speed by skipping frames in the video, by default this skips by 2 frames\ndepending on your video's FPS, "),
     sg.Button("-", size=(1, 1), key='-SKIP-', button_color=('white', 'darkred')),
     sg.Slider(range=(1, 100), default_value=15, orientation='h', size=(23, 10), trough_color="white",
               border_width=6,
               key='skip_frames',
               tooltip="This is in frames, you have the ability to skip 2-625 frames within the video"),
     sg.Button("+", size=(1, 1), key='-SKIP+', button_color=('white', 'darkgreen'))],
]

layout = [
    [sg.InputText(key="video_file", disabled=True, default_text=r"Select one or multiple video file(s) to edit *",
                  tooltip="The video(s) you want to be edited, make sure file names don't have ';' in them",
                  text_color='black'),
     sg.FilesBrowse()],
    # This file specification code will only work as an argument on Windows systems: file_types=(("Video Files", "*.mp4;*.avi;*.mkv;*.mov;*.wmv;*.flv;*.webm"),)
    [sg.InputText(key="output_folder", default_text=r"Select an output folder", disabled=True,
                  tooltip="The folder where you want the edited video to export", text_color='black'),
     sg.FolderBrowse()],
    [sg.pin(sg.Column(auto_montage_layout, key='-ROW3-', visible=True, pad=(0, 0)))],
    [sg.Text('Loading . . .', key='loading_text', visible=False, text_color='yellow')],
    [sg.Button("Edit Video", visible=True, button_color=('white', 'green')),
     sg.Button("Cancel", visible=False, button_color=('white', 'darkred'))],
    [sg.Button("Output Folder", visible=False, button_color=('black', 'lightblue'))]
]
# Create the window
window = sg.Window("Automatic Video Editing", layout, icon=base64_image)

last_update_time = 0

def progress_callback(message):
    global last_update_time
    import time
    current_time = time.time()
    # Only update GUI every 0.1 seconds to reduce overhead
    if current_time - last_update_time >= 0.1:
        last_update_time = current_time
        window.write_event_value('-PROGRESS-', message)

# Event loop
while True:
    event, values = window.read(timeout=200)
    if event == sg.WINDOW_CLOSED:
        if os.path.isdir("output_images"):
            shutil.rmtree("output_images")
        if os.path.exists("output_audio.wav"):
            os.remove("output_audio.wav")
        break
    if values['dropdown_audio'] == 'other':
        window['music_choice'].update(visible=True)
    else:
        window['music_choice'].update(visible=False)
    # Handle volume slider buttons
    if event == '-VOL-':
        new_vol = max(0, int(values['music_volume']) - 1)
        window['music_volume'].update(new_vol)
    elif event == '-VOL+':
        new_vol = min(200, int(values['music_volume']) + 1)
        window['music_volume'].update(new_vol)
    # Handle skip frames slider buttons
    elif event == '-SKIP-':
        new_skip = max(1, int(values['skip_frames']) - 1)
        window['skip_frames'].update(new_skip)
    elif event == '-SKIP+':
        new_skip = min(100, int(values['skip_frames']) + 1)
        window['skip_frames'].update(new_skip)
    if event == '-PROGRESS-':
        window['loading_text'].update(values[event], visible=True)
    try:
        if not run_thread.is_alive():
            filename1, extension1 = os.path.basename(values["video_file"]).split('.')
            new_filename = f"{filename1}_output.mp4"
            dualProcessFilePath = output2 + '/' + new_filename
            if run_next_thread:
                next_thread = threading.Thread(target=remove_silence_main,
                                               args=(dualProcessFilePath, output2, str(values["-THRESHOLD-"])))
                next_thread.start()
                next_thread.join()
                run_next_thread = False
                os.remove(dualProcessFilePath)
            window['Edit Video'].update(visible=True)
            window['Cancel'].update(visible=False)
            window['loading_text'].update(visible=False)
            window['Output Folder'].update(visible=True)
            shutil.rmtree("output_images")
            os.remove("output_audio.wav")
    except:
        pass
    if event == "Output Folder":
        if values["output_folder"] == 'Select an output folder':
            if ';' in values["video_file"]:
                output1 = os.path.dirname(values["video_file"].split(';')[0])
            else:
                output1 = os.path.dirname(values["video_file"])
        else:
            output1 = values["output_folder"]
        path_with_backslashes = output1.replace('/', '\\')
        if platform.system() == "Windows":
            subprocess.Popen(['explorer', path_with_backslashes])
        elif platform.system() == "Darwin":
            subprocess.Popen(['open', output1])
        else:
            try:
                subprocess.Popen(['xdg-open', output1])
            except FileNotFoundError:
                try:
                    subprocess.Popen(['nautilus', output1])
                except FileNotFoundError:
                    try:
                        subprocess.Popen(['dolphin', output1])
                    except FileNotFoundError:
                        try:
                            subprocess.Popen(['thunar', output1])
                        except FileNotFoundError:
                            print("Could not open directory. Please check your file manager installation.")
    if event == "Cancel":
        if os.path.isdir("output_images"):
            shutil.rmtree("output_images")
        os.kill(os.getpid(), signal.SIGINT)
    elif event == "Edit Video":
        if values["output_folder"] == 'Select an output folder':
            if ';' in values["video_file"]:
                first_path = values["video_file"].split(';')[0]
            else:
                first_path = values["video_file"]
            output2 = os.path.dirname(first_path)
        else:
            output2 = values["output_folder"]
        if values["video_file"] == "Select one or multiple video file(s) to edit *":
            sg.popup("Please select a video file.", title="Error", icon="ERROR")
        else:
            try:
                cls()
                run_thread = threading.Thread(target=auto_game_montage, args=(
                    values["video_file"], output2, values['dropdown_audio'], values['music_volume'],
                    values['which_game'], int(values['skip_frames']), values['effects_bool'],
                    ''), kwargs={'progress_callback': progress_callback})
                run_thread.start()
            except Exception as e:
                sg.popup(e, title="No highlights detected", icon="ERROR")
            window['Output Folder'].update(visible=False)
            window['Edit Video'].update(visible=False)
            window['Cancel'].update(visible=True)
            window['loading_text'].update(visible=True)
window.close()
