import argparse
from pubmed_module import fetch_and_save_papers

def main():
    parser = argparse.ArgumentParser(description="Fetch PubMed research papers based on a query.")
    parser.add_argument("query", type=str, help="PubMed search query")
    parser.add_argument("-f", "--file", type=str, help="Output CSV file path")
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug information")
    
    args = parser.parse_args()
    fetch_and_save_papers(args.query, args.file, args.debug)

if __name__ == "__main__":
    main()
