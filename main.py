# Import libraries
import RPi.GPIO as GPIO
import random
from ES2EEPROMUtils import ES2EEPROM
import os
import time
from gpiozero import Buzzer

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzerPin = 33
eeprom = None
Menu = False
end_of_game = None
guessNumber = 0
GameScore = 0
buz = None
acc = None
counter = 0
value = 0


# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game, value
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    index = 1
    for score in raw_data:
        print("{} -{} took {} guesses".format(index, score[0], score[1]))
        index += 1
    pass


# Setup Pins
def setup():
    global buz, acc, eeprom, Menu, name
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    eeprom = ES2EEPROM()

    # Setup regular GPIO
    GPIO.setup(LED[0], GPIO.OUT)
    GPIO.setup(LED[1], GPIO.OUT)
    GPIO.setup(LED[2], GPIO.OUT)
    GPIO.setup(LED_accuracy, GPIO.OUT)

    GPIO.output(LED[0], GPIO.LOW)
    GPIO.output(LED[1], GPIO.LOW)
    GPIO.output(LED[2], GPIO.LOW)
    GPIO.output(LED_accuracy, GPIO.LOW)
    GPIO.setup(buzzerPin, GPIO.OUT)

    # Setup PWM channel
    if buz is None:
        buz = GPIO.PWM(buzzerPin, 50)
    if acc is None:
        acc = GPIO.PWM(LED_accuracy, 50)

    buz.start(0)
    acc.start(0)
    #    Setup debouncing and callbacks
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=500)
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=500)

    pass


# Load high scores
def fetch_scores():
    global eeprom
    # get however many scores there are

    # Get the scores
    tempScores = []
    scores = ES2EEPROM.read_block(eeprom, 0, 13)
    score_count = scores[0]
    tempName = ""
    # convert the codes back to ascii
    for j in range(1, len(scores)):
        if j % 4 == 0:
            tempScores.append([tempName, scores[j]])
            tempName = ""
        else:
            tempName += chr(scores[j])
    scores = tempScores

    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    global GameScore, eeprom, name
    # fetch scores
    s_count, ss = fetch_scores()
    s_count += 1

    # include new score
    ss.append([name, GameScore])
    # sort
    ss.sort(key=lambda x: x[1])

    # update total amount of scores
    # wwrite new scores
    data_to_write = []
    data_to_write.append(s_count)
    for score in ss[0:3]:
        for letter in score[0]:
            data_to_write.append(ord(letter))
        data_to_write.append(score[1])
    ES2EEPROM.write_block(eeprom, 0, data_to_write)

    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3) - 1)


# Increase button pressed
def btn_increase_pressed(channel):
    global guessNumber
    print("increase")
    guessNumber += 1
    # Increase the value shown on the LEDs
    if (guessNumber > 7):
        guessNumber = 0
    if (guessNumber == 0):
        GPIO.output(LED[0], GPIO.LOW)
        GPIO.output(LED[1], GPIO.LOW)
        GPIO.output(LED[2], GPIO.LOW)
    if (guessNumber == 1):
        GPIO.output(LED[0], GPIO.LOW)
        GPIO.output(LED[1], GPIO.LOW)
        GPIO.output(LED[2], GPIO.HIGH)
    if (guessNumber == 2):
        GPIO.output(LED[0], GPIO.LOW)
        GPIO.output(LED[1], GPIO.HIGH)
        GPIO.output(LED[2], GPIO.LOW)
    if (guessNumber == 3):
        GPIO.output(LED[0], GPIO.LOW)
        GPIO.output(LED[1], GPIO.HIGH)
        GPIO.output(LED[2], GPIO.HIGH)
    if (guessNumber == 4):
        GPIO.output(LED[0], GPIO.HIGH)
        GPIO.output(LED[1], GPIO.LOW)
        GPIO.output(LED[2], GPIO.LOW)
    if (guessNumber == 5):
        GPIO.output(LED[0], GPIO.HIGH)
        GPIO.output(LED[1], GPIO.LOW)
        GPIO.output(LED[2], GPIO.HIGH)
    if (guessNumber == 6):
        GPIO.output(LED[0], GPIO.HIGH)
        GPIO.output(LED[1], GPIO.HIGH)
        GPIO.output(LED[2], GPIO.LOW)
    if (guessNumber == 7):
        GPIO.output(LED[0], GPIO.HIGH)
        GPIO.output(LED[1], GPIO.HIGH)
        GPIO.output(LED[2], GPIO.HIGH)

    # You can choose to have a global variable store the user's current guess,
    # or just pull the value off the LEDs when a user makes a guess
    pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    global guessNumber, answer, back, submit, Menu, GameScore, end_of_game, name, Brightness
    print("guess")
    start = time.time()
    submit = True
    back = False
    Menu = False
    while GPIO.input(btn_submit) == GPIO.LOW:
        time.sleep(0.01)
        length = time.time() - start
        if length > 1:
            print("returning to menu")
            GPIO.cleanup()

            setup()

            menu()
            back = True
            break

    # Compare the actual value with the user value displayed on the LEDs
    print("your guess was", guessNumber)
    # print("the answer was", value)
    if guessNumber != value and not Menu:
        # print("here")
        accuracy_leds()
        print("LED brightness is " + str(Brightness) + " %")
        #       trigger_buzzer()
        GameScore += 1
    elif guessNumber == value and not Menu:
        print("correct, you took " + str(GameScore) + " guesses")
        name = input("you won, whats your name? \n")
        name = name.upper()
        while not end_of_game:
            if len(name) < 3:
                name = input("must contain at least 3 letters \n")
                name = name.upper()

            else:
                name = name[0:3]
                save_scores()
                end_of_game = True

    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    pass


# LED Brightness
def accuracy_leds():
    global acc, submit, value, guessNumber, Brightness
    # Set the brightness of the LED based on how close the guess is to the answer
    Brightness = 0
    if (guessNumber < value) and (submit == True):
        Brightness = (guessNumber / value) * 100
        acc.start(Brightness)
    elif (guessNumber > value) and (submit == True):
        Brightness = ((8 - guessNumber) / (8 - value)) * 100
        acc.start(Brightness)
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    pass


# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    global buzzer, submit, buz, value, guessNumber
    offset = abs(value - guessNumber)
    buz.start(50)
    if (offset == 1) and (submit == True):
        buz.ChangeFrequency(4)
    elif (offset == 2) and (submit == True):
        buz.ChangeFrequency(2)
    elif (offset == 3) and (submit == True):
        buz.ChangeFrequency(1)
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()