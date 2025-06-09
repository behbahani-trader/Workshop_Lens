// Custom JavaScript for documentation

// Add copy button to code blocks
document.addEventListener('DOMContentLoaded', function() {
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(function(block) {
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.textContent = 'Copy';
        button.style.position = 'absolute';
        button.style.right = '0.5em';
        button.style.top = '0.5em';
        button.style.padding = '0.25em 0.5em';
        button.style.backgroundColor = '#f8f9fa';
        button.style.border = '1px solid #e1e4e5';
        button.style.borderRadius = '3px';
        button.style.cursor = 'pointer';
        button.style.fontSize = '0.8em';
        button.style.opacity = '0.7';
        button.style.transition = 'opacity 0.2s';

        button.addEventListener('mouseover', function() {
            button.style.opacity = '1';
        });

        button.addEventListener('mouseout', function() {
            button.style.opacity = '0.7';
        });

        button.addEventListener('click', function() {
            const text = block.textContent;
            navigator.clipboard.writeText(text).then(function() {
                button.textContent = 'Copied!';
                setTimeout(function() {
                    button.textContent = 'Copy';
                }, 2000);
            });
        });

        block.parentNode.style.position = 'relative';
        block.parentNode.appendChild(button);
    });
});

// Add table of contents to long pages
document.addEventListener('DOMContentLoaded', function() {
    const content = document.querySelector('.document');
    if (content) {
        const headings = content.querySelectorAll('h2, h3');
        if (headings.length > 3) {
            const toc = document.createElement('div');
            toc.className = 'toc';
            toc.style.margin = '1em 0';
            toc.style.padding = '1em';
            toc.style.backgroundColor = '#f8f9fa';
            toc.style.borderRadius = '4px';
            toc.style.border = '1px solid #e1e4e5';

            const tocTitle = document.createElement('h4');
            tocTitle.textContent = 'Table of Contents';
            toc.appendChild(tocTitle);

            const tocList = document.createElement('ul');
            tocList.style.listStyle = 'none';
            tocList.style.padding = '0';
            tocList.style.margin = '0';

            headings.forEach(function(heading) {
                const item = document.createElement('li');
                const link = document.createElement('a');
                link.textContent = heading.textContent;
                link.href = '#' + heading.id;
                link.style.textDecoration = 'none';
                link.style.color = '#2980b9';
                link.style.display = 'block';
                link.style.padding = '0.25em 0';
                link.style.marginLeft = (heading.tagName === 'H3' ? '1em' : '0');
                item.appendChild(link);
                tocList.appendChild(item);
            });

            toc.appendChild(tocList);
            content.insertBefore(toc, content.firstChild);
        }
    }
});

// Add search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.wy-side-nav-search input[type="text"]');
    if (searchInput) {
        searchInput.placeholder = 'Search documentation...';
        searchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    window.location.href = 'search.html?q=' + encodeURIComponent(query);
                }
            }
        });
    }
});

// Add dark mode toggle
document.addEventListener('DOMContentLoaded', function() {
    const header = document.querySelector('.wy-nav-top');
    if (header) {
        const toggle = document.createElement('button');
        toggle.className = 'dark-mode-toggle';
        toggle.textContent = '🌙';
        toggle.style.position = 'absolute';
        toggle.style.right = '1em';
        toggle.style.top = '50%';
        toggle.style.transform = 'translateY(-50%)';
        toggle.style.background = 'none';
        toggle.style.border = 'none';
        toggle.style.fontSize = '1.5em';
        toggle.style.cursor = 'pointer';
        toggle.style.padding = '0.5em';
        toggle.style.color = '#fff';

        toggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            toggle.textContent = document.body.classList.contains('dark-mode') ? '☀️' : '🌙';
        });

        header.appendChild(toggle);
    }
}); 