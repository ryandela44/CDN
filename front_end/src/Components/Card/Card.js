import React from "react";

const Card = (title,video,author,stats,onClick)=> {
    return (
         <div className="card" onClick={() => onClick({title, video, author, stats})}>
             <h3 className="card-title">{title}</h3>
             <img src={video} alt={title} className="card-video" />
             <div className="card-content">
                 <p className="card-author">{author}</p>
                 <p className="card-stats">{stats}</p>
            </div>
        </div>
    )
}

export default Card