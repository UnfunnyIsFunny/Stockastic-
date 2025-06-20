# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from striprtf.striprtf import rtf_to_text
import spacy
import pandas as pd
import os
TEXT_FILES_DIR = 'Training Data'
OUTPUT_CSV_FILE = 'structured_wsj_articles.csv'
SPACY_MODEL = 'en_core_web_sm'


def preprocess():
    try:
        nlp = spacy.load(SPACY_MODEL)
        print(f"Loaded spaCy model: {SPACY_MODEL}")
    except OSError:
        print(f"SpaCy model '{SPACY_MODEL}' not found. Downloading...")
        spacy.cli.download(SPACY_MODEL)
        nlp = spacy.load(SPACY_MODEL)
        print(f"Downloaded and loaded spaCy model: {SPACY_MODEL}")

    structured_data = []
    if not os.path.isdir(TEXT_FILES_DIR):
        print(f"Error: Directory '{TEXT_FILES_DIR}' not found. Please create it and place your text files inside.")
    else:
        file_count = 0
        for filename in os.listdir(TEXT_FILES_DIR):
            if filename.endswith('.txt'):
                filepath = os.path.join(TEXT_FILES_DIR, filename)
                file_count += 1
                print(
                    f"Processing file: {filename} ({file_count} / {len(os.listdir(TEXT_FILES_DIR)) if os.path.isdir(TEXT_FILES_DIR) else 0})")  # Basic progress indicator

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        article_text = f.read()

                    # --- 4. Process Text with spaCy ---
                    doc = nlp(article_text)

                    # --- 5. Extract Information ---
                    # A. Basic file info
                    article_id = filename.replace('.txt', '')  # Use filename as a unique ID

                    # B. Try to extract a date (common for news)
                    # This is a simple heuristic; a more robust date extractor might be needed
                    # It assumes the date is one of the first DATE entities found or in the filename
                    extracted_date = None
                    for ent in doc.ents:
                        if ent.label_ == 'DATE':
                            try:
                                # Attempt to parse as a date object for consistency
                                extracted_date = pd.to_datetime(ent.text, errors='coerce')
                                if pd.notna(extracted_date):  # Ensure it's a valid date
                                    break  # Take the first valid date found
                            except:
                                continue

                    # Fallback: if no date entity, try to parse from filename if it's structured like wsj_YYYY_MM_DD_XXX
                    if extracted_date is None and len(article_id.split('_')) >= 3 and article_id.split('_')[
                        1].isdigit() and article_id.split('_')[2].isdigit():
                        try:
                            extracted_date = pd.to_datetime(
                                f"{article_id.split('_')[1]}-{article_id.split('_')[2]}-{article_id.split('_')[3]}",
                                errors='coerce')
                        except:
                            pass  # Silently fail if filename date format isn't as expected

                    # C. Extract Companies (ORG entities)
                    companies = [ent.text for ent in doc.ents if ent.label_ == 'ORG']

                    # D. Extract People (PERSON entities)
                    people = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']

                    # E. Extract Locations (GPE/LOC entities)
                    locations = [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]

                    # F. Extract Sentences (useful for further analysis)
                    sentences = [sent.text for sent in doc.sents]

                    # G. Try to infer a title (e.g., first sentence or first line if clean)
                    # This is a very rough heuristic; true titles are better extracted during scraping
                    title = sentences[0] if sentences else ""
                    # Basic cleanup for title:
                    if len(title) > 150:  # Avoid very long first sentences as titles
                        title = title[:150] + "..."

                    # --- 6. Store Information ---
                    structured_data.append({
                        'Article_ID': article_id,
                        'Date': extracted_date,  # Will be NaT if no date found
                        'Title': title,
                        'Companies_Mentioned': list(set(companies)),  # Use set to get unique companies
                        'People_Mentioned': list(set(people)),
                        'Locations_Mentioned': list(set(locations)),
                        'Full_Text': article_text,
                        # You could add other fields here, e.g., 'Sentence_Count': len(sentences)
                    })

                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    # Optional: You might want to log these errors or store partial data

        # --- 7. Create and Save DataFrame ---
        if structured_data:
            df = pd.DataFrame(structured_data)

            # Convert Date column to datetime objects, handling errors
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

            print(f"\nSuccessfully processed {len(df)} articles.")
            df.to_csv(OUTPUT_CSV_FILE, index=False, encoding='utf-8')
            print(f"Structured data saved to {OUTPUT_CSV_FILE}")
            print("\nDataFrame Head:")
            print(df.head())
        else:
            print("No articles processed or no data collected.")
def union():

    article = pd.read_csv('structured_wsj_articles.csv')
    #print(article['Date'])
    for file in os.listdir('Stocks'):
        stock = pd.read_csv(f"Stocks/{file}")
        print(stock['Date'])
        merge = pd.concat((article, stock), axis=1)
        merge.to_csv(f'Training Set {file}')

        #print(merge)



    # Use a breakpoint in the code line below to debug your script.
    # print(f'Hi, {name}')  # Press Ctrl+8 to toggle the breakpoint.
    # try:
    #     with open('Training Data/Factiva-20250620-0646.rtf', 'r', encoding='utf-8') as f:
    #         rtf_content = f.read()
    #     plain_text = rtf_to_text(rtf_content)
    #     with open('Articles_4.txt', 'w', encoding='utf-8') as f_out:
    #         f_out.write(plain_text)
    #         print("Conversion successful!")
    # except Exception as e:
    #     print(f"Error during conversion: {e}")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #preprocess()
    union()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
