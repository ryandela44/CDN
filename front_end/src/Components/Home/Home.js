import React, {useEffect, useState} from "react";
import Header from "../Header/Header";
import Footer from "../Footer/Footer";
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import "./Home.css";

const Home = () => {
    const [videos, setVideos] = useState([]);

    useEffect(() => {
        const fetchVideos = async () => {
            try {
                const response = await fetch("https://localhost:9004/list_videos_metadata", {
                    method: "GET",
                    headers: {"Content-Type": "application/json"},
                });
                if (response.ok) {
                    const data = await response.json();
                    console.log("Fetched videos:", data); // Add this line for debugging
                    setVideos(data);
                } else {
                    console.error("Failed to fetch videos");
                }
            } catch (error) {
                console.error("Error fetching videos:", error);
            }
        };

        fetchVideos()
    }, []);


    const videoCard = (video) => (
        <a
            key={video.filename}
            href={`https://localhost:9004/video/${video.filename}`}
            style={{textDecoration: "none"}}
        >
            <div className="card" style={{cursor: "pointer"}}>
                <img src={video.thumbnail} alt={video.title} className="card-video"/>
                <h3 className="card-title">{video.title}</h3>
                <div className="card-content">
                    <p className="card-author">By: {video.author}</p>
                    <p className="card-stats">{video.stats}</p>
                </div>
            </div>
        </a>
    );

    return (
        <div className="home-container">
            <Header/>
            <div className="row">
                {videos.length === 0 ? (
                    <p>No videos available. Please check back later.</p>
                ) : (
                )}
            </div>
            <Footer/>
        </div>
    );
};

export default Home;