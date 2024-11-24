import React, { useEffect } from "react";

const VideoPlayer = ({ match }) => {
    const { filename } = match.params;

    useEffect(() => {
        // Optional: Preload video metadata
    }, [filename]);

    return (
        <div className="video-player">
            <video controls width="100%">
                <source src={`https://localhost:9004/video/${filename}`} type="video/mp4" />
                Your browser does not support the video tag.
            </video>
        </div>
    );
};

export default VideoPlayer;