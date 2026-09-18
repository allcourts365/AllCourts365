document.addEventListener("DOMContentLoaded", function() {
    // Check if we are on the 'change' form of a club to get the ID
    const match = window.location.pathname.match(/\/admin\/clubs\/club\/(\d+)\/change/);
    if (!match) {
        // If we are not editing an existing club (e.g. adding a new one or in the changelist), we can't show a full page preview easily.
        return;
    }
    
    const clubId = match[1];

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
    iframe.src = `/clubes/${clubId}/`;
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
        
        previewLabel.style.cursor = 'default';
        const contentDiv = document.getElementById('content');
        if (contentDiv) {
            // Injeção de CSS bruto para forçar a morte de QUALQUER buraco branco no topo
            // Isso aniquila padding-top e margin-top de todos os elementos entre o cabeçalho e a prévia, 
            // mas preserva o padding-left/right do #content (as bordas laterais).
            const antiGapStyle = document.createElement('style');
            antiGapStyle.innerHTML = `
                #main { padding-top: 0 !important; margin-top: 0 !important; }
                #content { padding-top: 0 !important; margin-top: 0 !important; }
                .breadcrumbs { padding-bottom: 0 !important; margin-bottom: 0 !important; border-bottom: none !important; }
                #content > h1 { display: none !important; margin: 0 !important; padding: 0 !important; height: 0 !important; }
                ul.messagelist { margin-bottom: 0 !important; }
                #sticky-page-preview { margin-top: 0 !important; }
            `;
            document.head.appendChild(antiGapStyle);

            // Insere a prévia dentro do #content, no topo
            contentDiv.insertBefore(previewContainer, contentDiv.firstChild);
            
            // Transforma o body para não rolar
            document.documentElement.style.overflow = 'hidden';
            document.body.style.overflow = 'hidden';
            
            // Cria um invólucro para o formulário rolar separadamente
            const scrollWrapper = document.createElement('div');
            scrollWrapper.style.overflowY = 'auto';
            scrollWrapper.style.height = `calc(100vh - 70px - ${previewHeightPx}px)`; 
            scrollWrapper.style.paddingTop = '15px'; // Espaço de ~0.5cm pedido pelo usuário
            
            // Move todos os elementos seguintes (o formulário) para dentro do invólucro
            while (previewContainer.nextSibling) {
                scrollWrapper.appendChild(previewContainer.nextSibling);
            }
            contentDiv.appendChild(scrollWrapper);
            
        } else {
            document.body.appendChild(previewContainer);
        }
    } else {
        document.body.appendChild(previewContainer);
    }

    // --- Drag Logic ---
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
                previewContainer.style.right = 'auto'; // override default right placement
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

    // --- Resize Logic ---
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

    // Inputs from the admin form
    const inputs = {
        name: document.getElementById('id_name'),
        address: document.getElementById('id_address'),
        description: document.getElementById('id_description'),
        cardImageSize: document.getElementById('id_card_image_size'),
        
        cardImage: document.getElementById('id_card_image'),
        bgImage: document.getElementById('id_background_image'),
        logo: document.getElementById('id_logo'),
        logoSize: document.getElementById('id_logo_size'),
        
        bgColor: document.getElementById('id_background_color'),
        overlayColor: document.getElementById('id_overlay_color'),
        overlayOpacity: document.getElementById('id_overlay_opacity'),
        highlightColor: document.getElementById('id_highlight_color'),
        titleColor: document.getElementById('id_title_color'),
        subtitleColor: document.getElementById('id_subtitle_color'),
    };

    // Helper to get initial image URLs from Django's clearable file input
    function getInitialImage(fieldClass) {
        const link = document.querySelector('.' + fieldClass + ' .file-upload a');
        return link ? link.href : null;
    }
    
    let currentImages = {
        card_image: getInitialImage('field-card_image'),
        background_image: getInitialImage('field-background_image'),
        logo: getInitialImage('field-logo')
    };

    // File reading
    function handleFileInput(input, key, callback) {
        if (!input) return;
        input.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    currentImages[key] = e.target.result;
                    callback();
                }
                reader.readAsDataURL(file);
            } else {
                currentImages[key] = null;
                callback();
            }
        });
    }

    // Checkboxes for clearing images
    function attachClearCheckbox(fieldClass, key, callback) {
        const cb = document.querySelector('.' + fieldClass + ' input[type="checkbox"]');
        if (cb) {
            cb.addEventListener('change', function() {
                if (this.checked) {
                    currentImages[key] = null;
                } else {
                    currentImages[key] = getInitialImage(fieldClass);
                }
                callback();
            });
        }
    }

    // Update iframe logic
    iframe.onload = function() {
        const iDoc = iframe.contentWindow.document;
        
        function updateIframe() {
            // Text fields
            if (inputs.name) {
                // Title is either a span or an anchor inside h1
                const h1 = iDoc.querySelector('h1');
                if (h1) {
                    const inner = h1.querySelector('a') || h1.querySelector('span');
                    if (inner) inner.textContent = inputs.name.value || 'Nome do Clube';
                }
            }
            if (inputs.description) {
                // Description is a paragraph after h1
                const h1 = iDoc.querySelector('h1');
                if (h1 && h1.nextElementSibling && h1.nextElementSibling.tagName === 'P' && !h1.nextElementSibling.querySelector('i')) {
                    h1.nextElementSibling.textContent = inputs.description.value;
                }
            }
            if (inputs.address) {
                // Address has a map marker icon
                const addrIcon = iDoc.querySelector('i.fa-map-marker-alt');
                if (addrIcon && addrIcon.parentNode) {
                    // Update text node next to icon
                    addrIcon.nextSibling.textContent = ' ' + (inputs.address.value || 'Endereço não informado');
                }
            }
            
            // Colors (CSS Variables)
            const root = iDoc.documentElement;
            if (inputs.bgColor && inputs.bgColor.value) root.style.setProperty('--bg-color', inputs.bgColor.value);
            if (inputs.overlayColor && inputs.overlayColor.value) root.style.setProperty('--overlay-color', inputs.overlayColor.value);
            if (inputs.overlayOpacity && inputs.overlayOpacity.value) root.style.setProperty('--overlay-opacity', inputs.overlayOpacity.value);
            if (inputs.highlightColor && inputs.highlightColor.value) root.style.setProperty('--highlight-color', inputs.highlightColor.value);
            if (inputs.titleColor && inputs.titleColor.value) root.style.setProperty('--title-color', inputs.titleColor.value);
            if (inputs.subtitleColor && inputs.subtitleColor.value) root.style.setProperty('--subtitle-color', inputs.subtitleColor.value);

            // Images
            // 1. Logo
            const logoContainer = iDoc.querySelector('.club-header-card > div:first-child > div:nth-child(2)');
            let logoImg = logoContainer ? logoContainer.querySelector('img') : iDoc.querySelector('.club-header-card img[style*="border-radius: 50%"]');
            if (logoImg) {
                if (currentImages.logo) {
                    logoImg.src = currentImages.logo;
                    logoImg.style.width = '100%';
                    logoImg.style.height = '100%';
                } else {
                    logoImg.src = '/static/bolinha.png';
                    logoImg.style.width = '60px';
                    logoImg.style.height = '60px';
                }
                const lSize = inputs.logoSize ? (parseInt(inputs.logoSize.value, 10) || 100) : 100;
                logoImg.style.transform = "scale(" + (lSize / 100) + ")";
                logoImg.style.transformOrigin = "center";
            }

            // 2. Header Cover Image
            const coverContainer = iDoc.querySelector('.club-header-card > div:first-child > div:first-child');
            let coverImg = null;
            if (coverContainer) {
                coverImg = coverContainer.querySelector('img');
                if (!coverImg && (currentImages.card_image || currentImages.background_image)) {
                    coverImg = iDoc.createElement('img');
                    coverImg.style.width = '100%';
                    coverImg.style.height = '100%';
                    coverImg.style.objectFit = 'contain';
                    coverImg.style.opacity = '0.5';
                    coverImg.style.transformOrigin = 'center';
                    coverContainer.appendChild(coverImg);
                }
            }
            if (coverImg) {
                if (currentImages.card_image) {
                    coverImg.src = currentImages.card_image;
                    coverImg.style.display = 'block';
                } else if (currentImages.background_image) {
                    coverImg.src = currentImages.background_image;
                    coverImg.style.display = 'block';
                } else {
                    coverImg.style.display = 'none';
                }
                
                // Size scale
                const sizeVal = inputs.cardImageSize ? (parseInt(inputs.cardImageSize.value, 10) || 100) : 100;
                coverImg.style.transform = "scale(" + (sizeVal / 100) + ")";
            }
            
            // 3. Body Background Image
            if (currentImages.background_image) {
                iDoc.body.style.setProperty('background-image', 'url(' + currentImages.background_image + ')', 'important');
            } else {
                iDoc.body.style.setProperty('background-image', 'none', 'important');
            }
            
            // Display percentage next to slider in admin
            if (inputs.cardImageSize) {
                let valDisplay = document.getElementById('card_size_display');
                if (!valDisplay) {
                    valDisplay = document.createElement('span');
                    valDisplay.id = 'card_size_display';
                    valDisplay.style.marginLeft = '10px';
                    valDisplay.style.fontWeight = 'bold';
                    valDisplay.style.color = '#fff';
                    inputs.cardImageSize.parentNode.appendChild(valDisplay);
                }
                valDisplay.textContent = inputs.cardImageSize.value + '%';
            }
            if (inputs.logoSize) {
                let logoValDisplay = document.getElementById('logo_size_display');
                if (!logoValDisplay) {
                    logoValDisplay = document.createElement('span');
                    logoValDisplay.id = 'logo_size_display';
                    logoValDisplay.style.marginLeft = '10px';
                    logoValDisplay.style.fontWeight = 'bold';
                    logoValDisplay.style.color = '#fff';
                    inputs.logoSize.parentNode.appendChild(logoValDisplay);
                }
                logoValDisplay.textContent = inputs.logoSize.value + '%';
            }
        }

        // Attach event listeners to text/number/color inputs
        Object.keys(inputs).forEach(k => {
            const el = inputs[k];
            if (el && el.type !== 'file') {
                el.addEventListener('input', updateIframe);
            }
        });

        // Attach file listeners
        handleFileInput(inputs.cardImage, 'card_image', updateIframe);
        handleFileInput(inputs.bgImage, 'background_image', updateIframe);
        handleFileInput(inputs.logo, 'logo', updateIframe);
        
        attachClearCheckbox('field-card_image', 'card_image', updateIframe);
        attachClearCheckbox('field-background_image', 'background_image', updateIframe);
        attachClearCheckbox('field-logo', 'logo', updateIframe);

        // Run once on load
        updateIframe();
    };
});
