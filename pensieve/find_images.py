import pickle
import requests
from .keys import BING_API_KEY
from .image import upload_image


def search_bing_for_image(query):
    """
    Perform a Bing image search.

    Args:
        query: Image search query

    Returns:
        results: List of image result JSON dicts
    """
    search_params = {'q': query,
                     'mkt': 'en-us',
                     'safeSearch': 'strict'}
    auth = {'Ocp-Apim-Subscription-Key': BING_API_KEY}
    url = 'https://api.cognitive.microsoft.com/bing/v5.0/images/search'
    r = requests.get(url, params=search_params, headers=auth)
    results = r.json()['value']
    return results


def store_best(search_results, n=1):
    """
    Store the top n results from a search in S3 bucket.

    Args:
        search_results: list of search result JSON dicts
        n: number of results to store

    Returns:
        urls: urls of images
        success: list of S3 upload success states
        full_key_names: list of uuids to store in imageURL
    """
    urls, success, full_key_names = [], [], []
    for i, result in enumerate(search_results):
        if i >= n:
            break
        urls.append(result['contentUrl'])
    for url in urls:
        s, fkn = upload_image(url)
        success.append(s)
        full_key_names.append(fkn)
    return urls, success, full_key_names


if __name__ == '__main__':
    try:
        with open('example_bing_result.pkl', 'rb') as f:
            results_json = pickle.load(f)
    except IOError:
        results_json = search_bing_for_image('wand')
        with open('example_bing_result.pkl', 'wb') as f:
            pickle.dump(results_json, f)

    results_list = results_json['value']
    best_urls, _, _ = store_best(results_list, n=3)
    print(best_urls)