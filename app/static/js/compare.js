document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM ready for diff2html integration");
    
    // Store versions data
    let promptVersions;
    try {
        // Get the data from the JSON script tag instead of inline parsing
        const versionsDataElement = document.getElementById('prompt-versions-data');
        promptVersions = versionsDataElement ? JSON.parse(versionsDataElement.textContent) : [];
        
        console.log("Parsed versions:", promptVersions.length);
        
        // Log a sample version to check property names
        if (promptVersions.length > 0) {
            console.log("Sample version object:", promptVersions[0]);
        }
        
        // Make versions available globally for debugging
        window.promptVersions = promptVersions;
    } catch(e) {
        console.error("Error parsing versions:", e);
        promptVersions = [];
    }
    
    // Create a map for easy access to version data
    const versionMap = {};
    promptVersions.forEach(version => {
        versionMap[version.version] = {
            id: version.id,
            name: version.name,
            // Use the actual property names from the data
            systemPrompt: version.system_prompt,
            userPrompt: version.user_prompt,
            isActive: version.is_active,
            createdAt: version.created_at,
            updatedAt: version.updated_at || version.created_at,
            createdBy: version.created_by,
            updatedBy: version.updated_by || version.created_by
        };
    });
    
    // Elements
    const version1Selector = document.getElementById('version1Selector');
    const version2Selector = document.getElementById('version2Selector');
    const compareButton = document.getElementById('compareButton');
    const comparisonResults = document.getElementById('comparisonResults');
    const loadingComparison = document.getElementById('loadingComparison');
    const comparisonError = document.getElementById('comparisonError');
    const sideBySideView = document.getElementById('sideBySideView');
    const inlineView = document.getElementById('inlineView');
    
    // View type (side-by-side or inline)
    let viewType = 'side-by-side';
    
    // Initialize the comparison UI
    if (compareButton && version1Selector && version2Selector) {
        compareButton.addEventListener('click', function() {
            const v1 = parseInt(version1Selector.value);
            const v2 = parseInt(version2Selector.value);
            
            if (v1 === v2) {
                showError("Please select different versions to compare");
                return;
            }
            
            compareVersions(v1, v2);
        });
    }
    
    // View toggle handlers
    if (sideBySideView && inlineView) {
        sideBySideView.addEventListener('click', function() {
            viewType = 'side-by-side';
            sideBySideView.classList.add('active');
            inlineView.classList.remove('active');
            // Re-run comparison with current versions
            const v1 = parseInt(version1Selector.value);
            const v2 = parseInt(version2Selector.value);
            compareVersions(v1, v2);
        });
        
        inlineView.addEventListener('click', function() {
            viewType = 'line-by-line';
            inlineView.classList.add('active');
            sideBySideView.classList.remove('active');
            // Re-run comparison with current versions
            const v1 = parseInt(version1Selector.value);
            const v2 = parseInt(version2Selector.value);
            compareVersions(v1, v2);
        });
    }
    
    // Compare versions function
    function compareVersions(v1, v2) {
        if (!comparisonResults || !loadingComparison) return;
        
        // Show loading, hide results
        comparisonResults.classList.add('d-none');
        loadingComparison.classList.remove('d-none');
        comparisonError.classList.add('d-none');
        
        try {
            const v1Data = versionMap[v1];
            const v2Data = versionMap[v2];
            
            if (!v1Data || !v2Data) {
                showError("Could not find version data");
                return;
            }
            
            // Debug the data
            console.log("Version 1 data:", v1Data);
            console.log("Version 2 data:", v2Data);
            
            // Safely access the fields with fallbacks
            const systemPrompt1 = v1Data.systemPrompt || "";
            const systemPrompt2 = v2Data.systemPrompt || "";
            const userPrompt1 = v1Data.userPrompt || "";
            const userPrompt2 = v2Data.userPrompt || "";
            
            // Debug the actual values we're working with
            console.log("System prompt 1:", typeof systemPrompt1, systemPrompt1.length);
            console.log("System prompt 2:", typeof systemPrompt2, systemPrompt2.length);
            console.log("User prompt 1:", typeof userPrompt1, userPrompt1.length);
            console.log("User prompt 2:", typeof userPrompt2, userPrompt2.length);
            
            // Create diff2html configurations
            const diffConfig = {
                drawFileList: false,
                matching: 'lines',
                outputFormat: viewType,
                renderNothingWhenEmpty: true,
                matchWordsThreshold: 0.25,
                matchingMaxComparisons: 3000,
                // Custom templates to hide the RENAMED label
                rawTemplates: {
                    'tag-file-renamed': '',
                    'generic-file-path-renamed': '<span class="d2h-file-name">{% raw %}{{{fileName}}}{% endraw %}</span>'
                }
            };
            
            // Generate diffs and render them with diff2html
            
            // // Name diff
            // const nameDiffInput = createDiffInput(
            //     `Version ${v1} Name.txt`,
            //     `Version ${v2} Name.txt`,
            //     v1Data.name || "",
            //     v2Data.name || ""
            // );
            // document.getElementById('nameCompare').innerHTML = 
            //     Diff2Html.html(nameDiffInput, diffConfig);
            
            // System prompt diff
            const systemPromptDiffInput = createDiffInput(
                `Version ${v1} System Prompt`,
                `Version ${v2} System Prompt`,
                systemPrompt1,
                systemPrompt2
            );
            console.log("System prompt diff input:", systemPromptDiffInput);
            document.getElementById('systemPromptCompare').innerHTML = 
                Diff2Html.html(systemPromptDiffInput, diffConfig);
            
            // User prompt diff
            const userPromptDiffInput = createDiffInput(
                `Version ${v1} User Prompt`,
                `Version ${v2} User Prompt`,
                userPrompt1,
                userPrompt2
            );
            console.log("User prompt diff input:", userPromptDiffInput);
            document.getElementById('userPromptCompare').innerHTML = 
                Diff2Html.html(userPromptDiffInput, diffConfig);
            
            // Show results, hide loading
            comparisonResults.classList.remove('d-none');
            loadingComparison.classList.add('d-none');
            
        } catch (error) {
            console.error("Error comparing versions:", error);
            showError("Error comparing versions: " + error.message);
        }
    }
    
    // Helper function to create a unified diff input for diff2html
    function createDiffInput(oldFileName, newFileName, oldText, newText) {
        // Ensure we have string values and normalize line endings
        oldText = String(oldText || "").replace(/\r\n/g, '\n').replace(/\r/g, '\n');
        newText = String(newText || "").replace(/\r\n/g, '\n').replace(/\r/g, '\n');
        
        // Check if one is empty and one has content (added or removed entirely)
        const isAddition = oldText.trim() === "" && newText.trim() !== "";
        const isDeletion = oldText.trim() !== "" && newText.trim() === "";
        
        // Split into lines and ensure we have at least one line
        // If text is empty, make it a single empty line for proper diff formatting
        const oldLines = oldText.trim() === "" ? [""] : oldText.split('\n');
        const newLines = newText.trim() === "" ? [""] : newText.split('\n');
        
        // Debug line counts 
        console.log(`${oldFileName} lines: ${oldLines.length}, ${newFileName} lines: ${newLines.length}`);
        console.log(`Is addition: ${isAddition}, Is deletion: ${isDeletion}`);
        
        // Create a unified diff header with correct line counts
        // Ensure we use at least 1 for the line count
        // Use identical paths in the diff-git line to avoid RENAMED tag
        const commonName = oldFileName.replace(/ \(v[0-9]+\)$/, '');
        const header = [
            'diff --git a/' + oldFileName + ' b/' + newFileName,
            '--- a/' + oldFileName,
            '+++ b/' + newFileName,
            '@@ -1,' + Math.max(1, oldLines.length) + ' +1,' + Math.max(1, newLines.length) + ' @@'
        ].join('\n');
        
        // Build the diff body with proper formatting
        let diffBody = '';
        
        // If texts are identical, show them as context
        if (oldText === newText && oldText.length > 0) {
            for (const line of oldLines) {
                diffBody += ' ' + line + '\n';
            }
        }
        // If this is a pure addition (nothing to empty)
        else if (isAddition) {
            diffBody += '-\n';  // Show an empty line being removed
            for (const line of newLines) {
                diffBody += '+' + line + '\n';
            }
        }
        // If this is a pure deletion (empty to nothing)
        else if (isDeletion) {
            for (const line of oldLines) {
                diffBody += '-' + line + '\n';
            }
            diffBody += '+\n';  // Show an empty line being added
        }
        // Otherwise show the normal differences
        else {
            for (const line of oldLines) {
                diffBody += '-' + line + '\n';
            }
            for (const line of newLines) {
                diffBody += '+' + line + '\n';
            }
        }
        
        // Debug the diff output
        if (diffBody.length < 500) {
            console.log("Generated diff:", diffBody);
        } else {
            console.log("Generated diff (truncated):", diffBody.substring(0, 200) + "...");
        }
        
        // Return the complete unified diff format
        return header + '\n' + diffBody;
    }
    
    // Helper to show error messages
    function showError(message) {
        if (!comparisonError) return;
        
        const errorMessageElement = document.getElementById('errorMessage');
        if (errorMessageElement) {
            errorMessageElement.textContent = message;
        }
        
        comparisonResults.classList.add('d-none');
        loadingComparison.classList.add('d-none');
        comparisonError.classList.remove('d-none');
    }
    
    // Check if we should compare on load (if compare tab is active)
    if (window.location.hash === '#compare-tab-pane' || 
        new URLSearchParams(window.location.search).get('tab') === 'compare') {
        // Activate the compare tab
        const compareTab = document.getElementById('compare-tab');
        if (compareTab) {
            const bsTab = new bootstrap.Tab(compareTab);
            bsTab.show();
            
            // Short delay to ensure tab is shown before triggering comparison
            setTimeout(function() {
                if (version1Selector && version2Selector) {
                    const v1 = parseInt(version1Selector.value);
                    const v2 = parseInt(version2Selector.value);
                    if (v1 !== v2) {
                        compareVersions(v1, v2);
                    }
                }
            }, 200);
        }
    }
});