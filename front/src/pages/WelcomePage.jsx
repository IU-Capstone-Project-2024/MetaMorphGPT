import styles from "./WelcomePage.module.css";
import {ReactComponent as UserLogo} from "../img/userLogo.svg";
import {ReactComponent as Search} from "../img/search.svg";
import Cookies from 'js-cookie';
import {useState} from "react";

const WelcomePage = (props) => {
    const [inputValue, setInputValue] = useState('');

    const handleInputChange = (event) => {
        setInputValue(event.target.value);
        props.setModelSearch(event.target.value);
    };
    return <div className={styles.welcomePageBlock}>
        <div className={styles.topBlock}>
            <div className={styles.userData}>
                <p>Welcome Back,</p>
                <div className={styles.userBlock}>
                    <UserLogo />
                    <span>{Cookies.get("user_name")}</span>
                </div>
            </div>
            <div className={styles.searchBlock}>
                <Search />
                <input
                    type="text"
                    placeholder="Search For Models"
                    value={inputValue}
                    onChange={handleInputChange}
                />
            </div>
        </div>
        <div className={styles.descriptionBlock}>
            <p>
             MetaMorphGPT is an innovative AI-driven tool <br/>
                That allows you to load your chat conversations with anyone,
                enabling the model to train on that chat and mimic the speech style of the individual. <br/>
                With MetaMorphGPT, you can engage in conversations that feel personal and tailored, <br/>
                seamlessly continuing chats in the distinctive voice of the original speaker.
            <br/><br/>
            How to use it: <br/>
            1) Choose or Create a Model: Start by selecting an existing model or create your own by uploading a chat conversation. <br/>
            2) Copy the Model Token: Once your model is ready, you will receive a unique token. Copy this token. <br/>
                3) Engage via Telegram: Open your Telegram app and go to the bot <a href="https://t.me/meta_morph_gpt_bot" style={{textDecoration: "underline"}}> @meta_morph_gpt_bot. </a> <br/>
            4) Paste the Token: Paste the copied token into the chat with the bot to activate your personalized conversation. <br/>
            </p>
        </div>
    </div>
}

export {WelcomePage};