/**
 * Prompt version comparison functionality
 * Handles the comparison between different versions of prompts
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Compare script loaded');
    
    // Listen for Bootstrap tab events
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tabEl => {
        tabEl.addEventListener('shown.bs.tab', function (event) {
            console.log('Tab activated:', event.target.getAttribute('data-bs-target'));
            
            // If compare tab is activated, initialize our code
            if (event.target.getAttribute('data-bs-target') === '#compare-tab-pane') {
                console.log('Compare tab activated, initializing compare functionality');
                // Wait a brief moment for tab content to be fully rendered
                setTimeout(initCompareFeature, 100);
            }
        });
    });

    // Try to handle direct navigation to the compare tab
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('tab') === 'compare') {
        console.log('URL indicates compare tab, activating tab');
        const compareTab = document.getElementById('compare-tab');
        if (compareTab) {
            compareTab.click();
        }
    }
    
    // Initialize compare feature immediately as well
    initCompareFeature();
    
    // Expose compareVersions function globally so it can be called from inline HTML
    window.manualCompareVersions = function() {
        try {
            console.log('Manual compare versions called');
            
            // Get the necessary elements
            const version1Select = document.getElementById('version1');
            const version2Select = document.getElementById('version2');
            const comparisonResult = document.getElementById('comparisonResult');
            
            if (!version1Select || !version2Select || !comparisonResult) {
                console.error('Missing required elements for comparison');
                return;
            }
            
            // Show a loading indicator
            comparisonResult.innerHTML = '<div class="alert alert-info text-center p-4"><div class="spinner-border spinner-border-sm me-2" role="status"></div> Comparing versions...</div>';
            comparisonResult.style.display = 'block';
            
            // Get the selected versions
            const v1 = parseInt(version1Select.value);
            const v2 = parseInt(version2Select.value);
            
            if (v1 === v2) {
                comparisonResult.innerHTML = '<div class="alert alert-warning text-center"><i class="bi bi-exclamation-triangle me-2"></i> Please select different versions to compare</div>';
                return;
            }
            
            // Check if we have versions data
            if (!window.promptVersions || !Array.isArray(window.promptVersions) || window.promptVersions.length < 2) {
                comparisonResult.innerHTML = '<div class="alert alert-danger text-center"><i class="bi bi-exclamation-triangle me-2"></i> Need at least 2 versions to compare</div>';
                return;
            }
            
            // Check if diff library is loaded
            if (!window.Diff) {
                comparisonResult.innerHTML = '<div class="alert alert-danger text-center"><i class="bi bi-exclamation-triangle me-2"></i> Diff library not loaded. Please refresh the page and try again.</div>';
                return;
            }
            
            // Execute the actual comparison
            setTimeout(function() {
                try {
                    // Create a proper comparison UI with the versions
                    executeComparison(v1, v2);
                } catch (error) {
                    console.error('Error executing comparison:', error);
                    comparisonResult.innerHTML = '<div class="alert alert-danger text-center"><i class="bi bi-exclamation-triangle me-2"></i> Error comparing versions: ' + error.message + '</div>';
                }
            }, 50);
        } catch (error) {
            console.error('Error in manual compare function:', error);
            alert('Error comparing versions: ' + error.message);
        }
    };
    
    // Function to execute the actual comparison
    function executeComparison(v1, v2) {
        console.log('Executing comparison of versions', v1, v2);
        
        // Map of version data for easy lookup
        let versionData = {};
        window.promptVersions.forEach(version => {
            versionData[version.version] = {
                systemPrompt: version.system_prompt,
                userPrompt: version.user_prompt,
                isActive: version.is_active
            };
        });
        
        // Get comparison result container
        const comparisonResult = document.getElementById('comparisonResult');
        
        // Reset the comparison result UI
        comparisonResult.innerHTML = `
        <div class="comparison-container">
            <div class="row">
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <span id="version1Title">Version <span id="v1Num"></span></span>
                            <span id="version1Badge" class="badge bg-success">Active</span>
                        </div>
                        <div class="card-body">
                            <h6 class="mb-2">System Prompt</h6>
                            <div id="version1System" class="prompt-section mb-4"></div>
                            
                            <h6 class="mb-2">User Prompt</h6>
                            <div id="version1User" class="prompt-section"></div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <span id="version2Title">Version <span id="v2Num"></span></span>
                            <span id="version2Badge" class="badge bg-secondary d-none">Active</span>
                        </div>
                        <div class="card-body">
                            <h6 class="mb-2">System Prompt</h6>
                            <div id="version2System" class="prompt-section highlight-changes mb-4"></div>
                            
                            <h6 class="mb-2">User Prompt</h6>
                            <div id="version2User" class="prompt-section highlight-changes"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-3 text-center">
            <a href="#" id="setActiveBtn" class="btn btn-sm btn-outline-primary">Set Version <span id="setActiveVersion"></span> as Active</a>
        </div>`;
        
        // Set version numbers in UI
        document.getElementById('v1Num').textContent = v1;
        document.getElementById('v2Num').textContent = v2;
        
        // Get version data
        const v1Data = versionData[v1] || { systemPrompt: '', userPrompt: '' };
        const v2Data = versionData[v2] || { systemPrompt: '', userPrompt: '' };
        
        // Display version 1 data (left side)
        document.getElementById('version1System').textContent = v1Data.systemPrompt;
        document.getElementById('version1User').textContent = v1Data.userPrompt;
        
        // Update active badge visibility
        document.getElementById('version1Badge').classList.toggle('d-none', !v1Data.isActive);
        document.getElementById('version2Badge').classList.toggle('d-none', !v2Data.isActive);
        
        // Create diffs
        if (typeof Diff.diffWords === 'function') {
            // Using jsdiff library
            // Create diffs for system prompt
            const systemDiff = Diff.diffWords(v1Data.systemPrompt, v2Data.systemPrompt);
            let systemHtml = '';
            systemDiff.forEach(part => {
                if (part.added) {
                    systemHtml += `<ins>${part.value}</ins>`;
                } else if (part.removed) {
                    systemHtml += `<del>${part.value}</del>`;
                } else {
                    systemHtml += part.value;
                }
            });
            
            // Create diffs for user prompt
            const userDiff = Diff.diffWords(v1Data.userPrompt, v2Data.userPrompt);
            let userHtml = '';
            userDiff.forEach(part => {
                if (part.added) {
                    userHtml += `<ins>${part.value}</ins>`;
                } else if (part.removed) {
                    userHtml += `<del>${part.value}</del>`;
                } else {
                    userHtml += part.value;
                }
            });
            
            // Set diff display for version 2 (right side)
            document.getElementById('version2System').innerHTML = systemHtml;
            document.getElementById('version2User').innerHTML = userHtml;
        } else {
            // Fallback to direct text
            document.getElementById('version2System').textContent = v2Data.systemPrompt;
            document.getElementById('version2User').textContent = v2Data.userPrompt;
        }
        
        // Set up active version button
        const setActiveBtn = document.getElementById('setActiveBtn');
        const setActiveVersion = document.getElementById('setActiveVersion');
        
        if (!v2Data.isActive && setActiveVersion && setActiveBtn) {
            setActiveVersion.textContent = v2;
            setActiveBtn.href = window.setActiveVersionUrl.replace('VERSION_NUMBER', v2);
            setActiveBtn.classList.remove('d-none');
        } else if (setActiveBtn) {
            setActiveBtn.classList.add('d-none');
        }
        
        console.log('Version comparison completed successfully');
    }
    
    // Use a self-executing function to isolate our code from potential external interference
    function initCompareFeature() {
        try {
            console.log('initCompareFeature called');
            // Version comparison elements
            const compareBtn = document.getElementById('compareBtn');
            const version1Select = document.getElementById('version1');
            const version2Select = document.getElementById('version2');
            const swapVersionsBtn = document.getElementById('swapVersionsBtn');
            const comparisonResult = document.getElementById('comparisonResult');
            const setActiveBtn = document.getElementById('setActiveBtn');
            
            console.log('Compare button found:', !!compareBtn);
            console.log('Version selects found:', !!version1Select, !!version2Select);
            console.log('Swap button found:', !!swapVersionsBtn);
            console.log('Comparison result div found:', !!comparisonResult);
            
            // Ensure we have all the necessary elements
            if (!compareBtn || !version1Select || !version2Select || !comparisonResult) {
                console.error('Missing required elements for comparison functionality');
                return;
            }
            
            // Initialize comparison data from the versions passed from the template
            let versionData = {};
            
            // Create a map of version data for easy lookup
            if (window.promptVersions && Array.isArray(window.promptVersions)) {
                console.log('Found prompt versions:', window.promptVersions.length);
                
                if (window.promptVersions.length < 2) {
                    console.warn('Need at least 2 versions to compare, but only found', window.promptVersions.length);
                    if (compareBtn) {
                        compareBtn.disabled = true;
                        compareBtn.title = "Need at least 2 versions to compare";
                    }
                }
                
                window.promptVersions.forEach(version => {
                    versionData[version.version] = {
                        systemPrompt: version.system_prompt,
                        userPrompt: version.user_prompt,
                        isActive: version.is_active
                    };
                });
            } else {
                console.error('window.promptVersions is not available or not an array:', window.promptVersions);
            }
            
            // Setup event listeners
            if (compareBtn) {
                console.log("Adding click handler to compare button in main script");
                
                // Try multiple approaches to ensure the click handler works
                // 1. Standard event listener
                compareBtn.addEventListener('click', handleCompareClick);
                
                // 2. Direct onclick property as backup
                compareBtn.onclick = function(e) {
                    console.log("Compare button clicked via onclick property");
                    handleCompareClick(e);
                    return false;
                };
                
                // 3. jQuery-style event binding if jQuery is available
                if (window.jQuery) {
                    console.log("jQuery detected, adding jQuery event handler");
                    jQuery(compareBtn).on('click', handleCompareClick);
                }
            }
            
            if (swapVersionsBtn) {
                swapVersionsBtn.addEventListener('click', function(e) {
                    console.log('Swap button clicked');
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const temp = version1Select.value;
                    version1Select.value = version2Select.value;
                    version2Select.value = temp;
                    
                    // Add a small delay to ensure we're not competing with other scripts
                    setTimeout(function() {
                        compareVersions();
                    }, 50);
                    
                    return false;
                });
            }
            
            // Compare the selected versions
            function compareVersions() {
                console.log('compareVersions called');
                
                try {
                    // Show a loading indicator
                    if (comparisonResult) {
                        comparisonResult.innerHTML = '<div class="alert alert-info text-center p-4"><div class="spinner-border spinner-border-sm me-2" role="status"></div> Comparing versions...</div>';
                        comparisonResult.style.display = 'block';
                    }
                    
                    const v1 = parseInt(version1Select.value);
                    const v2 = parseInt(version2Select.value);
                    
                    console.log('Comparing versions:', v1, v2);
                    
                    if (v1 === v2) {
                        comparisonResult.innerHTML = '<div class="alert alert-warning text-center"><i class="bi bi-exclamation-triangle me-2"></i> Please select different versions to compare</div>';
                        return;
                    }
                    
                    if (!window.promptVersions || !Array.isArray(window.promptVersions) || window.promptVersions.length < 2) {
                        comparisonResult.innerHTML = '<div class="alert alert-danger text-center"><i class="bi bi-exclamation-triangle me-2"></i> Need at least 2 versions to compare</div>';
                        return;
                    }
                    
                    if (!Diff) {
                        comparisonResult.innerHTML = '<div class="alert alert-danger text-center"><i class="bi bi-exclamation-triangle me-2"></i> Diff library not loaded. Please refresh the page and try again.</div>';
                        return;
                    }
                    
                    // Reset comparison result to original HTML structure from the template
                    resetComparisonResult();
                    
                    // Show the comparison result container
                    comparisonResult.style.display = 'block';
                    
                    // Set version numbers in UI
                    const v1NumEl = document.getElementById('v1Num');
                    const v2NumEl = document.getElementById('v2Num');
                    console.log('Version number elements found:', !!v1NumEl, !!v2NumEl);
                    
                    if (v1NumEl) v1NumEl.textContent = v1;
                    if (v2NumEl) v2NumEl.textContent = v2;
                    
                    // Set version texts
                    const v1Data = versionData[v1] || { systemPrompt: '', userPrompt: '' };
                    const v2Data = versionData[v2] || { systemPrompt: '', userPrompt: '' };
                    console.log('Version data found:', !!v1Data, !!v2Data);
                    
                    // Display version 1 data (left side)
                    const version1System = document.getElementById('version1System');
                    const version1User = document.getElementById('version1User');
                    console.log('Version 1 elements found:', !!version1System, !!version1User);
                    
                    if (version1System) version1System.textContent = v1Data.systemPrompt;
                    if (version1User) version1User.textContent = v1Data.userPrompt;
                    
                    // Update active badge visibility
                    const version1Badge = document.getElementById('version1Badge');
                    const version2Badge = document.getElementById('version2Badge');
                    console.log('Badge elements found:', !!version1Badge, !!version2Badge);
                    
                    if (version1Badge) version1Badge.classList.toggle('d-none', !v1Data.isActive);
                    if (version2Badge) version2Badge.classList.toggle('d-none', !v2Data.isActive);
                    
                    // Create diffs for system prompt
                    console.log('Creating diffs using Diff:', !!Diff);
                    
                    try {
                        // Check which Diff API we have available
                        if (typeof Diff.diffWords === 'function') {
                            console.log('Using Diff.diffWords API');
                            createDiffWithJsDiff(v1Data, v2Data);
                        } else if (typeof Diff.diffChars === 'function') {
                            console.log('Using Diff.diffChars API');
                            createDiffWithDiffJs(v1Data, v2Data);
                        } else {
                            console.error('No compatible Diff API found. Available methods:', Object.keys(Diff));
                            // Show error
                            comparisonResult.innerHTML = '<div class="alert alert-danger text-center"><i class="bi bi-exclamation-triangle me-2"></i> Diff library API not compatible. Please contact support.</div>';
                            return;
                        }
                        
                        // Set up active version button
                        const setActiveVersion = document.getElementById('setActiveVersion');
                        console.log('Set active elements found:', !!setActiveVersion, !!setActiveBtn);
                        
                        if (!v2Data.isActive && setActiveVersion && setActiveBtn) {
                            setActiveVersion.textContent = v2;
                            setActiveBtn.href = window.setActiveVersionUrl.replace('VERSION_NUMBER', v2);
                            setActiveBtn.classList.remove('d-none');
                        } else if (setActiveBtn) {
                            setActiveBtn.classList.add('d-none');
                        }
                        
                        console.log('Version comparison completed successfully');
                    } catch (diffError) {
                        console.error('Error during diff calculation:', diffError);
                        comparisonResult.innerHTML = '<div class="alert alert-danger text-center"><i class="bi bi-exclamation-triangle me-2"></i> Error creating diff: ' + diffError.message + '</div>';
                    }
                } catch (error) {
                    console.error('Error in compareVersions function:', error);
                    if (comparisonResult) {
                        comparisonResult.innerHTML = '<div class="alert alert-danger text-center"><i class="bi bi-exclamation-triangle me-2"></i> Error comparing versions: ' + error.message + '</div>';
                        comparisonResult.style.display = 'block';
                    }
                }
            }
            
            function handleCompareClick(e) {
                console.log('Compare button clicked - handler triggered');
                if (e) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                
                // Add a small delay to ensure we're not competing with other scripts
                setTimeout(function() {
                    compareVersions();
                }, 50);
                
                return false;
            }
            
            // Function to reset comparison result to original structure
            function resetComparisonResult() {
                // We need to preserve the original HTML structure
                const originalHTML = `
                <div class="comparison-container">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card mb-4">
                                <div class="card-header d-flex justify-content-between align-items-center">
                                    <span id="version1Title">Version <span id="v1Num"></span></span>
                                    <span id="version1Badge" class="badge bg-success">Active</span>
                                </div>
                                <div class="card-body">
                                    <h6 class="mb-2">System Prompt</h6>
                                    <div id="version1System" class="prompt-section mb-4"></div>
                                    
                                    <h6 class="mb-2">User Prompt</h6>
                                    <div id="version1User" class="prompt-section"></div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="card mb-4">
                                <div class="card-header d-flex justify-content-between align-items-center">
                                    <span id="version2Title">Version <span id="v2Num"></span></span>
                                    <span id="version2Badge" class="badge bg-secondary d-none">Active</span>
                                </div>
                                <div class="card-body">
                                    <h6 class="mb-2">System Prompt</h6>
                                    <div id="version2System" class="prompt-section highlight-changes mb-4"></div>
                                    
                                    <h6 class="mb-2">User Prompt</h6>
                                    <div id="version2User" class="prompt-section highlight-changes"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-3 text-center">
                    <a href="#" id="setActiveBtn" class="btn btn-sm btn-outline-primary">Set Version <span id="setActiveVersion"></span> as Active</a>
                </div>`;
                
                if (comparisonResult) {
                    comparisonResult.innerHTML = originalHTML;
                }
            }
            
            // For jsdiff library (4.x)
            function createDiffWithJsDiff(v1Data, v2Data) {
                // Create diffs for system prompt
                const systemDiff = Diff.diffWords(v1Data.systemPrompt, v2Data.systemPrompt);
                let systemHtml = '';
                systemDiff.forEach(part => {
                    if (part.added) {
                        systemHtml += `<ins>${part.value}</ins>`;
                    } else if (part.removed) {
                        systemHtml += `<del>${part.value}</del>`;
                    } else {
                        systemHtml += part.value;
                    }
                });
                
                // Create diffs for user prompt
                const userDiff = Diff.diffWords(v1Data.userPrompt, v2Data.userPrompt);
                let userHtml = '';
                userDiff.forEach(part => {
                    if (part.added) {
                        userHtml += `<ins>${part.value}</ins>`;
                    } else if (part.removed) {
                        userHtml += `<del>${part.value}</del>`;
                    } else {
                        userHtml += part.value;
                    }
                });
                
                // Set diff display for version 2 (right side)
                const version2System = document.getElementById('version2System');
                const version2User = document.getElementById('version2User');
                
                if (version2System) version2System.innerHTML = systemHtml;
                if (version2User) version2User.innerHTML = userHtml;
            }
            
            // For diff library (5.x)
            function createDiffWithDiffJs(v1Data, v2Data) {
                // Create diffs for system prompt
                const systemDiff = Diff.diffChars(v1Data.systemPrompt, v2Data.systemPrompt);
                let systemHtml = '';
                systemDiff.forEach(part => {
                    if (part.added) {
                        systemHtml += `<ins>${part.value}</ins>`;
                    } else if (part.removed) {
                        systemHtml += `<del>${part.value}</del>`;
                    } else {
                        systemHtml += part.value;
                    }
                });
                
                // Create diffs for user prompt
                const userDiff = Diff.diffChars(v1Data.userPrompt, v2Data.userPrompt);
                let userHtml = '';
                userDiff.forEach(part => {
                    if (part.added) {
                        userHtml += `<ins>${part.value}</ins>`;
                    } else if (part.removed) {
                        userHtml += `<del>${part.value}</del>`;
                    } else {
                        userHtml += part.value;
                    }
                });
                
                // Set diff display for version 2 (right side)
                const version2System = document.getElementById('version2System');
                const version2User = document.getElementById('version2User');
                
                if (version2System) version2System.innerHTML = systemHtml;
                if (version2User) version2User.innerHTML = userHtml;
            }
        } catch (error) {
            console.error('Error initializing compare functionality:', error);
        }
    }
}); 