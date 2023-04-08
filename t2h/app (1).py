from flask import Flask, render_template, request, send_file
from PIL import Image
from fpdf import FPDF
import random

app = Flask(__name__)

BG = Image.open("font/bg.png")
sizeOfSheet = BG.width
gap, _ = 0, 0

allowedChars = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM, .-?!() 1234567890'

def write(char):
    global gap, _

    if char == '\n':
        pass
    elif char == 'space':
        gap += 40
    else:
        char.lower()
        cases = Image.open("font/%s.png" % char)
        BG.paste(cases, (gap, _))
        size = cases.width
        gap += size
        del cases


def write_word(word):
    global gap, _
    if gap > sizeOfSheet - 95 * (len(word)):
        gap = 0
        _ += 200

    for letter in word:
        if letter in allowedChars:
            if letter.isupper():
                letter = letter.lower()
                letter += 'upper'
            elif letter == '.':
                letter = "fullstop"
            elif letter == '!':
                letter = 'exclamation'
            elif letter == '?':
                letter = 'question'
            elif letter == ',':
                letter = 'comma'
            elif letter == '(':
                letter = 'braketop'
            elif letter == ')':
                letter = 'braketcl'
            elif letter == '-':
                letter = 'hiphen'

            write(letter)

            # Add a random space to place letters randomly across the width of the image.
            xs = random.randint(10, 15)
            gap += xs

    # Add a space of random width after every word.
    xs = random.randint(50, 100)
    gap += xs



def worddd(input_text):
    global gap, _
    words_list = input_text.split(' ')
    for word in words_list:
        if '\n' in word:
            # make gap 0 and increase _ to move cursor to next line
            write_word(word.split('\n')[0])
            gap = 0
            _ += 200
            write_word(word.split('\n')[1])
        else:
            write_word(word)

        write('space')


def generate_pdf_text(data):
    global BG, gap, _

    l = len(data)
    nn = len(data) // 600

    chunks, chunk_size = len(data), len(data) // (nn + 1)
    p = [data[i:i + chunk_size] for i in range(0, chunks, chunk_size)]

    imagelist = []

    # iterate over chunks and append space at the end of each chunk to add new line
    for i in range(len(p)):
        p[i] += ' '

    # join chunks using '\n' separator to add new line between each chunk
    data_with_newlines = '\n'.join(p)

    # call worddd function to convert text into image and save temporary image files
    worddd(data_with_newlines)

    BG.save(f"0outt.png")
    imagelist.append("0outt.png")

    BG1 = Image.open("font/bg.png")
    BG = BG1
    gap = 0
    _ = 0

    pdf = FPDF()

    # create new page and add image to it sequentially
    for image in imagelist:
        pdf.add_page()
        pdf.image(image, 0, 0, 210, 297)

    pdf.output("output.pdf", "F")

    for image in imagelist:
        Image.open(image).close()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    input_text = request.form['text']

    generate_pdf_text(input_text)

    return send_file('output.pdf', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
