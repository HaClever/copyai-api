from bs4 import BeautifulSoup
from mitmproxy import ctx

# Load in the javascript to inject.
with open('injected.js', 'r') as f:
    injected_javascript = f.read()

def response(flow):
    # Only process 200 responses of HTML content.
    if 'Content-Type' in flow.response.headers:
        if flow.response.headers['Content-Type'] != 'text/html':
            return
        if not flow.response.status_code == 200:
            return

        # Inject a script tag containing the JavaScript.
        html = BeautifulSoup(flow.response.text, 'lxml')
        container = html.head or html.body
        if container:
            script = html.new_tag('script', type='text/javascript')
            script.string = injected_javascript
            container.insert(0, script)
            flow.response.text = str(html)

            ctx.log.info('Successfully injected the `injected.js` script.')
