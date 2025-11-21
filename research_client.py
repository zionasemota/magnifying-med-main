"""
Research API client for fetching real papers from PubMed, OpenAlex, and arXiv
"""

import requests
import time
from typing import Dict, Any, List, Optional
from urllib.parse import quote


class ResearchClient:
    """Client for fetching research papers from various APIs"""
    
    def __init__(self):
        self.pubmed_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.openalex_base = "https://api.openalex.org"
        self.arxiv_base = "http://export.arxiv.org/api/query"
        self.request_delay = 0.1  # Rate limiting
        self.timeout = 30  # Increased timeout to 30 seconds
        self.max_retries = 2  # Retry failed requests
    
    def search_pubmed(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search PubMed for papers
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of paper dictionaries
        """
        try:
            # Search for papers
            search_url = f"{self.pubmed_base}/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "sort": "relevance"
            }
            
            time.sleep(self.request_delay)
            response = requests.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            pmids = data.get("esearchresult", {}).get("idlist", [])
            if not pmids:
                return []
            
            # Fetch paper details
            fetch_url = f"{self.pubmed_base}/efetch.fcgi"
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(pmids[:max_results]),
                "retmode": "xml"
            }
            
            time.sleep(self.request_delay)
            fetch_response = requests.get(fetch_url, params=fetch_params, timeout=self.timeout)
            fetch_response.raise_for_status()
            
            # Parse XML (simplified - you might want to use a proper XML parser)
            papers = []
            xml_content = fetch_response.text
            
            # Simple parsing - extract titles and abstracts
            import re
            articles = re.findall(r'<PubmedArticle>(.*?)</PubmedArticle>', xml_content, re.DOTALL)
            
            for article in articles[:max_results]:
                try:
                    title_match = re.search(r'<ArticleTitle>(.*?)</ArticleTitle>', article, re.DOTALL)
                    abstract_match = re.search(r'<AbstractText.*?>(.*?)</AbstractText>', article, re.DOTALL)
                    pmid_match = re.search(r'<PMID.*?>(.*?)</PMID>', article)
                    
                    if title_match:
                        title = title_match.group(1).strip()
                        # Clean up XML entities
                        title = title.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
                        
                        abstract = ""
                        if abstract_match:
                            abstract = abstract_match.group(1).strip()
                            abstract = abstract.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
                        
                        pmid = ""
                        if pmid_match:
                            pmid = pmid_match.group(1).strip()
                        
                        paper = {
                            "title": title,
                            "abstract": abstract,
                            "pmid": pmid,
                            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}" if pmid else "",
                            "source": "pubmed"
                        }
                        papers.append(paper)
                except Exception as e:
                    # Skip articles that fail to parse
                    continue
            
            return papers
            
        except Exception as e:
            print(f"Error searching PubMed: {str(e)}")
            return []
    
    def search_openalex(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search OpenAlex for papers
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of paper dictionaries
        """
        for attempt in range(self.max_retries + 1):
            try:
                search_url = f"{self.openalex_base}/works"
                params = {
                    "search": query,
                    "per_page": min(max_results, 200),  # OpenAlex allows up to 200 per page
                    "page": 1,
                    "sort": "relevance_score:desc"
                }
                
                time.sleep(self.request_delay)
                response = requests.get(search_url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                break  # Success, exit retry loop
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    print(f"OpenAlex timeout, retrying ({attempt + 1}/{self.max_retries})...")
                    time.sleep(1)
                    continue
                else:
                    print(f"Error searching OpenAlex: Timeout after {self.max_retries + 1} attempts")
                    return []
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit (unlikely but handle it)
                    if attempt < self.max_retries:
                        wait_time = 2 * (attempt + 1)  # Shorter backoff for OpenAlex
                        print(f"OpenAlex rate limited (429), waiting {wait_time}s before retry ({attempt + 1}/{self.max_retries})...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"Error searching OpenAlex: Rate limited (429) after {self.max_retries + 1} attempts")
                        return []
                else:
                    print(f"Error searching OpenAlex: HTTP {e.response.status_code}")
                    return []
            except Exception as e:
                print(f"Error searching OpenAlex: {str(e)}")
                return []
        
        # Process the data if we got it
        if data is None:
            return []
        
        try:
            papers = []
            results = data.get("results", [])
            if not isinstance(results, list):
                return []
            
            for paper_data in results[:max_results]:
                if not paper_data or not isinstance(paper_data, dict):
                    continue
                
                # Extract authors
                authors_list = paper_data.get("authorships", [])
                authors = []
                for authorship in authors_list:
                    if isinstance(authorship, dict):
                        author = authorship.get("author", {})
                        if isinstance(author, dict):
                            display_name = author.get("display_name", "")
                            if display_name:
                                authors.append(display_name)
                
                # Extract publication year
                publication_date = paper_data.get("publication_date", "")
                year = None
                if publication_date:
                    try:
                        year = int(publication_date.split("-")[0])
                    except:
                        pass
                
                # Get primary location (venue/journal)
                primary_location = paper_data.get("primary_location", {})
                source = primary_location.get("source", {})
                venue = source.get("display_name", "") if source else ""
                
                # Get abstract
                abstract = paper_data.get("abstract", "")
                # OpenAlex abstracts are sometimes inverted, check for that
                if abstract and abstract.startswith("InvertedAbstract"):
                    abstract = ""
                
                paper = {
                    "title": paper_data.get("title", ""),
                    "abstract": abstract,
                    "url": paper_data.get("doi", "") or paper_data.get("id", ""),
                    "year": year,
                    "authors": authors,
                    "venue": venue,
                    "citations": paper_data.get("cited_by_count", 0),
                    "source": "openalex"
                }
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            print(f"Error processing OpenAlex results: {str(e)}")
            return []
    
    def search_arxiv(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search arXiv for papers
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of paper dictionaries
        """
        try:
            search_url = self.arxiv_base
            params = {
                "search_query": query,
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
            
            time.sleep(self.request_delay)
            response = requests.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse XML
            import xml.etree.ElementTree as ET
            try:
                root = ET.fromstring(response.content)
            except ET.ParseError:
                return []
            
            papers = []
            entries = root.findall("{http://www.w3.org/2005/Atom}entry")
            
            for entry in entries[:max_results]:
                try:
                    title = entry.find("{http://www.w3.org/2005/Atom}title")
                    summary = entry.find("{http://www.w3.org/2005/Atom}summary")
                    link = entry.find("{http://www.w3.org/2005/Atom}id")
                    
                    paper = {
                        "title": title.text.strip() if title is not None and title.text else "",
                        "abstract": summary.text.strip() if summary is not None and summary.text else "",
                        "url": link.text.strip() if link is not None and link.text else "",
                        "source": "arxiv"
                    }
                    if paper["title"]:  # Only add if we have a title
                        papers.append(paper)
                except Exception:
                    continue
            
            return papers
            
        except Exception as e:
            print(f"Error searching arXiv: {str(e)}")
            return []
    
    def search_all(self, query: str, max_results_per_source: int = 20) -> List[Dict[str, Any]]:
        """
        Search all available sources (continues even if some sources fail)
        
        Args:
            query: Search query
            max_results_per_source: Max results from each source
            
        Returns:
            Combined list of papers from all sources
        """
        all_papers = []
        
        # Search PubMed (medical focus) - continue even if it fails
        try:
            pubmed_papers = self.search_pubmed(query, max_results_per_source)
            all_papers.extend(pubmed_papers)
        except Exception as e:
            print(f"PubMed search failed, continuing with other sources: {str(e)}")
        
        # Search OpenAlex (comprehensive academic papers) - continue even if it fails
        try:
            openalex_papers = self.search_openalex(query, max_results_per_source)
            all_papers.extend(openalex_papers)
        except Exception as e:
            print(f"OpenAlex search failed, continuing with other sources: {str(e)}")
        
        # Search arXiv (preprints) - continue even if it fails
        try:
            arxiv_papers = self.search_arxiv(query, max_results_per_source)
            all_papers.extend(arxiv_papers)
        except Exception as e:
            print(f"arXiv search failed, continuing with other sources: {str(e)}")
        
        # Remove duplicates based on title similarity
        unique_papers = self._deduplicate_papers(all_papers)
        
        return unique_papers[:max_results_per_source * 3]  # Limit total results
    
    def _deduplicate_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate papers based on title similarity"""
        seen_titles = set()
        unique = []
        
        for paper in papers:
            title_lower = paper.get("title", "").lower().strip()
            # Simple deduplication - check if we've seen a very similar title
            is_duplicate = False
            for seen in seen_titles:
                # Check if titles are very similar (simple approach)
                if title_lower and seen:
                    # If one title contains most of the other, consider it duplicate
                    words_title = set(title_lower.split())
                    words_seen = set(seen.split())
                    if len(words_title) > 0 and len(words_seen) > 0:
                        similarity = len(words_title & words_seen) / max(len(words_title), len(words_seen))
                        if similarity > 0.8:  # 80% word overlap
                            is_duplicate = True
                            break
            
            if not is_duplicate and title_lower:
                seen_titles.add(title_lower)
                unique.append(paper)
        
        return unique
    
    def format_papers_for_llm(self, papers: List[Dict[str, Any]], max_papers: int = 30) -> str:
        """
        Format papers into a string for LLM consumption
        
        Args:
            papers: List of paper dictionaries
            max_papers: Maximum number of papers to include
            
        Returns:
            Formatted string
        """
        if not papers:
            return "No papers found."
        
        formatted = []
        for i, paper in enumerate(papers[:max_papers], 1):
            title = paper.get("title", "Unknown")
            abstract = paper.get("abstract", "")[:500]  # Truncate long abstracts
            url = paper.get("url", "")
            source = paper.get("source", "unknown")
            year = paper.get("year", "")
            
            paper_str = f"{i}. {title}"
            if year:
                paper_str += f" ({year})"
            if abstract:
                paper_str += f"\n   Abstract: {abstract}..."
            if url:
                paper_str += f"\n   URL: {url}"
            paper_str += f"\n   Source: {source}"
            
            formatted.append(paper_str)
        
        return "\n\n".join(formatted)


