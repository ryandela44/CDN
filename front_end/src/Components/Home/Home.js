import Header from "../Header/Header";
import Footer from "../Footer/Footer"
import Card from "../Card/Card";
import Slider from "react-slick"

const handleCardClick = () => {

}

const Home = () => {
    return (
        <div className={"home-container"}>
            <Header/>
            <div className="row">
                <Slider>
                    <Card title="" video="" author="" stats="" onClick={() =>handleCardClick()} ></Card>
                    <Card title="" video="" author="" stats="" onClick={() =>handleCardClick()} ></Card>
                    <Card title="" video="" author="" stats="" onClick={() =>handleCardClick()} ></Card>
                    <Card title="" video="" author="" stats="" onClick={() =>handleCardClick()} ></Card>
                    <Card title="" video="" author="" stats="" onClick={() =>handleCardClick()} ></Card>
                </Slider>
            </div>
            <Footer/>
        </div>
    )
}

export default Home