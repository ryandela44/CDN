import React from "react";
import "./Card.css"; // Ensure you import styles if you separate them

const Card = ({ title, video, author, stats, onClick }) => {
    return (
        <div className="card" onClick={onClick}>
            <img src={video} alt={title} className="card-video" />
            <h3 className="card-title">{title}</h3>
            <div className="card-content">
                <p className="card-author">By: {author}</p>
                <p className="card-stats">{stats}</p>
            </div>
        </div>
    );
};

export default Card;