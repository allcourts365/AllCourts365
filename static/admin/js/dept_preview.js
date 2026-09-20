document.addEventListener("DOMContentLoaded", function() {
    const match = window.location.pathname.match(/\/admin\/clubs\/department\/(\d+)\/change/);
    if (!match) return;
    const deptId = match[1];

    const clubSelect = document.getElementById('id_club');
    if (!clubSelect) return;
    let clubId = clubSelect.value;
    if (!clubId) return;

    // Create the container for the miniature
    const previewContainer = document.createElement('div');
    previewContainer.id = 'sticky-page-preview';
    previewContainer.style.position = 'fixed';
    
    // Virtual resolution of the iframe
    const virtualWidth = 1440;
    const virtualHeight = 900;
    
    // Load saved settings or use defaults
    let previewWidth = parseInt(localStorage.getItem('admin_preview_width')) || (virtualWidth * 0.3333);
    let currentScale = previewWidth / virtualWidth;
    let previewLeft = localStorage.getItem('admin_preview_left');
    let previewTop = localStorage.getItem('admin_preview_top');
    
    if (previewLeft !== null && previewTop !== null) {
        previewContainer.style.left = previewLeft + 'px';
        previewContainer.style.top = previewTop + 'px';
    } else {
        previewContainer.style.top = '120px';
        previewContainer.style.right = '40px';
    }
    
    previewContainer.style.width = previewWidth + 'px';
    previewContainer.style.height = (virtualHeight * currentScale) + 'px';
    previewContainer.style.zIndex = '9999';
    previewContainer.style.boxShadow = '0 10px 30px rgba(0,0,0,0.5)';
    previewContainer.style.borderRadius = '10px';
    previewContainer.style.overflow = 'hidden';
    previewContainer.style.backgroundColor = '#1a1a2e';
    previewContainer.style.border = '2px solid rgba(255,255,255,0.1)';

    const previewLabel = document.createElement('div');
    previewLabel.textContent = 'Prévia da Página (Ao Vivo) - Arraste-me';
    previewLabel.style.position = 'absolute';
    previewLabel.style.top = '0';
    previewLabel.style.left = '0';
    previewLabel.style.width = '100%';
    previewLabel.style.padding = '8px';
    previewLabel.style.textAlign = 'center';
    previewLabel.style.fontWeight = 'bold';
    previewLabel.style.color = '#fff';
    previewLabel.style.background = 'rgba(44, 44, 84, 0.9)';
    previewLabel.style.zIndex = '10';
    previewLabel.style.backdropFilter = 'blur(5px)';
    previewLabel.style.cursor = 'move';
    previewLabel.style.userSelect = 'none';

    // Create the iframe
    const iframe = document.createElement('iframe');
    iframe.src = `/clubes/${clubId}/departamento/${deptId}/`;
    iframe.style.width = virtualWidth + 'px';
    iframe.style.height = virtualHeight + 'px';
    iframe.style.border = 'none';
    iframe.style.transform = `scale(${currentScale})`;
    iframe.style.transformOrigin = 'top left';
    iframe.style.pointerEvents = 'none';

    // Create Resize Handle
    const resizeHandle = document.createElement('div');
    resizeHandle.style.position = 'absolute';
    resizeHandle.style.right = '0';
    resizeHandle.style.bottom = '0';
    resizeHandle.style.width = '20px';
    resizeHandle.style.height = '20px';
    resizeHandle.style.cursor = 'se-resize';
    resizeHandle.style.zIndex = '20';
    resizeHandle.innerHTML = '<svg viewBox="0 0 10 10" style="width:100%; height:100%;"><polygon points="10,0 10,10 0,10" fill="rgba(255,255,255,0.7)"/></svg>';

    previewContainer.appendChild(previewLabel);
    previewContainer.appendChild(iframe);
    previewContainer.appendChild(resizeHandle);

    const isMobile = window.innerWidth <= 768;
    if (isMobile) {
        previewContainer.style.position = 'relative';
        previewContainer.style.width = '100%';
        previewContainer.style.left = '0';
        previewContainer.style.margin = '0';
        previewContainer.style.zIndex = '999';
        previewContainer.style.borderRadius = '0';
        previewContainer.style.boxShadow = '0 5px 15px rgba(0,0,0,0.5)';
        
        const newWidth = window.innerWidth;
        currentScale = newWidth / virtualWidth;
        const previewHeightPx = (virtualHeight * currentScale) + 35;
        previewContainer.style.height = previewHeightPx + 'px'; 
        iframe.style.transform = `scale(${currentScale})`;
        
        const contentDiv = document.getElementById('content-main');
        const scrollWrapper = document.querySelector('.form-scroll-wrapper');
        
        if (scrollWrapper) {
            scrollWrapper.insertBefore(previewContainer, scrollWrapper.firstChild);
            
            const h1 = scrollWrapper.querySelector('h1');
            if (h1) h1.style.display = 'none';
        } else if (contentDiv) {
            contentDiv.insertBefore(previewContainer, contentDiv.firstChild);
        } else {
            document.body.appendChild(previewContainer);
        }
    } else {
        document.body.appendChild(previewContainer);
    }

    // Drag Logic
    let isDragging = false;
    let dragOffsetX, dragOffsetY;

    if (!isMobile) {
        previewLabel.addEventListener('mousedown', function(e) {
            isDragging = true;
            const rect = previewContainer.getBoundingClientRect();
            dragOffsetX = e.clientX - rect.left;
            dragOffsetY = e.clientY - rect.top;
        });

        document.addEventListener('mousemove', function(e) {
            if (isDragging) {
                let newX = e.clientX - dragOffsetX;
                let newY = e.clientY - dragOffsetY;
                previewContainer.style.left = newX + 'px';
                previewContainer.style.top = newY + 'px';
                previewContainer.style.right = 'auto';
            }
        });

        document.addEventListener('mouseup', function(e) {
            if (isDragging) {
                isDragging = false;
                localStorage.setItem('admin_preview_left', parseInt(previewContainer.style.left));
                localStorage.setItem('admin_preview_top', parseInt(previewContainer.style.top));
            }
        });
    }

    // Resize Logic
    let isResizing = false;
    let resizeStartWidth, resizeStartX;

    if (!isMobile) {
        resizeHandle.addEventListener('mousedown', function(e) {
            e.stopPropagation();
            e.preventDefault();
            isResizing = true;
            resizeStartWidth = parseInt(previewContainer.style.width);
            resizeStartX = e.clientX;
        });

        document.addEventListener('mousemove', function(e) {
            if (isResizing) {
                let diff = e.clientX - resizeStartX;
                let newWidth = Math.max(300, Math.min(virtualWidth, resizeStartWidth + diff));
                currentScale = newWidth / virtualWidth;
                previewContainer.style.width = newWidth + 'px';
                previewContainer.style.height = (virtualHeight * currentScale) + 'px';
                iframe.style.transform = `scale(${currentScale})`;
            }
        });

        document.addEventListener('mouseup', function(e) {
            if (isResizing) {
                isResizing = false;
                localStorage.setItem('admin_preview_width', parseInt(previewContainer.style.width));
            }
        });
    }

    // Inputs
    const inputs = {
        name: document.getElementById('id_name'),
        imageSize: document.getElementById('id_image_size'),
        image: document.getElementById('id_image'),
    };

    function getInitialImage(fieldClass) {
        const link = document.querySelector('.' + fieldClass + ' .file-upload a');
        return link ? link.href : null;
    }
    
    let currentImage = getInitialImage('field-image');

    if (inputs.image) {
        inputs.image.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    currentImage = e.target.result;
                    updateIframe();
                }
                reader.readAsDataURL(file);
            } else {
                currentImage = null;
                updateIframe();
            }
        });
    }

    const clearCb = document.querySelector('.field-image input[type="checkbox"]');
    if (clearCb) {
        clearCb.addEventListener('change', function() {
            if (this.checked) {
                currentImage = null;
            } else {
                currentImage = getInitialImage('field-image');
            }
            updateIframe();
        });
    }

    iframe.onload = function() {
        updateIframe();
    }
    
    function updateIframe() {
        if (!iframe.contentWindow) return;
        const iDoc = iframe.contentWindow.document;
        
        if (inputs.name) {
            const h1s = iDoc.querySelectorAll('h1');
            h1s.forEach(h1 => {
                if (h1.textContent.toUpperCase().includes(inputs.name.defaultValue.toUpperCase()) || h1.textContent.toUpperCase() === inputs.name.value.toUpperCase()) {
                     h1.textContent = inputs.name.value;
                }
            });
        }
        
        const coverImg = iDoc.querySelector('.club-header-card > div:first-child > div:first-child img');
        if (coverImg) {
            if (currentImage) {
                coverImg.src = currentImage;
                coverImg.style.display = 'block';
            }
            if (inputs.imageSize) {
                coverImg.style.transform = `scale(calc(${inputs.imageSize.value} / 100))`;
            }
        }
    }

    if (inputs.name) inputs.name.addEventListener('input', updateIframe);
    if (inputs.imageSize) inputs.imageSize.addEventListener('input', updateIframe);
});
