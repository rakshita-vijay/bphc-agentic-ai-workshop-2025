import os, sys, math, re, csv, pypdf, datetime, shutil

from _101_download_to_device import download_file, delete_pycache

# from crewai_toolkits_gem_2point0_flash._002_article_summarizer import gen_summary

from _002_article_summarizer import gen_summary
from _003_article_generator import gen_article

l_only_line_demarcator = "\n{}".format("~" * 120)
r_only_line_demarcator = "{}\n".format("~" * 120)
l_and_r_line_demarcator = "\n{}\n".format("~" * 120)

def main():
  print("\nWhat are you here to do?")
  print("1. Article Title Generator")
  print("2. Article Generator")
  print("3. Exit \n")

  repeat = 'yes'
  purpose_of_visit = 0
  while repeat == 'yes' or purpose_of_visit < 1 or purpose_of_visit > 3:
    try:
      purpose_of_visit = int(input(f"Enter a valid choice (1-3): "))
      repeat = 'no'
    except ValueError as ve:
      repeat = 'yes'
      print("\nInvalid input. Please enter a valid integer choice.")

  print(l_and_r_line_demarcator)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  if purpose_of_visit == 1:
    gen_summary()
    print(l_only_line_demarcator)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  elif purpose_of_visit == 2:
    gen_article()
    print(l_only_line_demarcator)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  # Exit
  elif purpose_of_visit == 3:
    delete_pycache()
    print("Exiting...")
    sys.exit(1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  continue_or_not = 'd'
  while continue_or_not.lower()[0] != 'y' and continue_or_not.lower()[0] != 'n':
    continue_or_not = input("\nWould you like to make more changes? Enter 'y' for yes and 'n' for no: ")

  c_or_e = continue_or_not.lower()[0]

  if c_or_e == 'y':
    print(l_only_line_demarcator)
    delete_pycache()
    main()
  else:
    delete_pycache()
    print("\nExiting...")
    sys.exit(1)

if __name__ == "__main__":
  main()
