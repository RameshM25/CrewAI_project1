```mermaid
graph TD
    %% 1. Create the Nodes (Your Agents)
    Start([User Inputs Content Topic])
    Web[🕵️‍♂️ Web Research Agent]
    YT[📺 YouTube Research Agent]
    Writer[✍️ LinkedIn Post Writer Agent]
    Image[🎨 Image Generator Agent]
    Final([✅ Final LinkedIn Post + Image])

    %% 2. Connect them together
    Start -->|Assigns Topic| Web
    Start -->|Assigns Topic| YT
    
    Web -->|Sends Articles & Trends| Writer
    YT -->|Sends Video Transcripts & Summaries| Writer
    
    Writer -->|Sends Post Concept for Visuals| Image
    
    Writer -->|Final Text| Final
    Image -->|Final Graphic| Final

    %% 3. Define the Colors
    classDef input fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff;
    classDef researcher fill:#3b82f6,stroke:#2563eb,stroke-width:2px,color:#fff;
    classDef creator fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff;
    classDef output fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff;

    %% 4. Apply Colors to Nodes Safely
    class Start input;
    class Web,YT researcher;
    class Writer,Image creator;
    class Final output;