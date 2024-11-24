import React, { useEffect, useState } from "react";
import Header from "../Header/Header";
import Footer from "../Footer/Footer";
import Card from "../Card/Card";
import Slider from "react-slick";
import "./Home.css";

const Home = () => {
    const [videos, setVideos] = useState([]);

    useEffect(() => {
        const fetchVideos = async () => {
            try {
                const response = await fetch("https://localhost:9004/list_videos_metadata", {
                    method: "GET",
                    headers: { "Content-Type": "application/json" },
                });
                if (response.ok) {
                    const data = await response.json();
                    setVideos(data);
                } else {
                    console.error("Failed to fetch videos");
                }
            } catch (error) {
                console.error("Error fetching videos:", error);
            }
        };

        fetchVideos();
    }, []);

    const handleCardClick = (video) => {
        window.location.href = `https://localhost:9004/video/${video.filename}`;
    };

    const sliderSettings = {
        dots: true,
        infinite: true,
        speed: 500,
        slidesToShow: 3,
        slidesToScroll: 1,
        responsive: [
            {
                breakpoint: 768,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 1,
                },
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                },
            },
        ],
    };

    return (
        <div className="home-container">
            <Header />
            <div className="row">
                <Slider {...sliderSettings}>
                    {videos.map((video, index) => (
                        <div key={index}>
                            <Card
                                title={video.title}
                                video={video.thumbnail}
                                author={video.author}
                                stats={video.stats}
                                onClick={() => handleCardClick(video)}
                            />
                        </div>
                    ))}
                </Slider>
            </div>
            <Footer />
        </div>
    );
};

export default Home;