import os
import argparse
import sys
import threading
import time
from PyPDF2 import PdfReader


def welcome():

    print(r'''     ____  ____  ___________                      __
    / __ \/ __ \/ ____/ ___/___  ____ ___________/ /_
   / /_/ / / / / /_   \__ \/ _ \/ __ `/ ___/ ___/ __ \
  / ____/ /_/ / __/  ___/ /  __/ /_/ / /  / /__/ / / /
 /_/   /_____/_/    /____/\___/\__,_/_/   \___/_/ /_/
                                                     ''')

def parse_args():
    parser = argparse.ArgumentParser(
        prog='PDF-Search.py',
        description='A simple yet effective tool that searches .pdf files for a keyword & returns the filename'
    )

    parser.add_argument('-d', '--directory-path', dest='dir_path', metavar='Directory Path', type=str,
                        help=r'Directory Path. Example: "C:\Documents\Example\PDF"')
    parser.add_argument('-k', '--keyword', dest='key_word', metavar='Keyword', type=str,
                        help='Keyword. Example: "Search Term"')

    parser.set_defaults(dir_path=False, key_word=False)

    args = parser.parse_args(sys.argv[1:])
    arg_errors = arg_error_check(args)

    if len(arg_errors) > 0:
        for error in arg_errors:
            print(f"[-] {error}\n")
        parser.print_help()
        sys.exit(1)

    for attr in vars(args):
        value = getattr(args, attr)
        if value is not None and not int:
            # Remove quotes
            cleaned_value = value.replace('"', '').replace("'", "")
            setattr(args, attr, cleaned_value)

    return args

def arg_error_check(args):
    arg_errors = []

    expected_args = {'dir_path', 'key_word'}
    for arg_name, arg_value in vars(args).items():
        if arg_name not in expected_args and arg_value is not False:
            arg_errors.append('Argument Error. Example PDF-Search.py -d <directory-path> -k <keyword/search term>')
            return arg_errors
        if arg_value is False:
            arg_errors.append('Missing argument Example PDF-Search.py -d <directory-path> -k <keyword/search term>')
            return arg_errors

    return arg_errors

def running_animation():
    animation = "|/-\\"
    i = 0
    while True:
        sys.stdout.write( "\r" + f"["  + animation[i % len(animation)] + "] ")
        sys.stdout.flush()
        i += 1
        time.sleep(1)

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"[!] Error reading {file_path}: {e}")
        return ""

def search_keyword_in_pdfs(dir, keyword):
    """Searches for a keyword in all PDF files in the directory."""
    results = []
    for file_name in os.listdir(dir):
        if file_name.endswith('.pdf'):
            file_path = os.path.join(dir, file_name)
            text = extract_text_from_pdf(file_path)
            if keyword.lower() in text.lower():
                snippet_start = text.lower().find(keyword.lower())
                snippet = text[snippet_start:snippet_start + 400]
                results.append((file_name, snippet))  # File name and snippet
    return results

if __name__ == "__main__":

    welcome()
    args = parse_args()


    if not os.path.exists(args.dir_path):
        print("[!] The specified directory does not exist.")
    else:
        animation_thread = threading.Thread(target=running_animation, daemon=True)
        animation_thread.start()

        matches = search_keyword_in_pdfs(args.dir_path, args.key_word)

        if matches:
            print(f'\n\n[+] Found {len(matches)} matches for "{args.key_word}":\n')
            for match in matches:
                print(f"\n[+] File: {match[0]}\n[*] Snippet:\n\n {match[1]}")
        else:
            print("\n[-] No matches found.")
