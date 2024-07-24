import styles from "./ModelCreationPage.module.css"
import {ReactComponent as CloseUserData} from "../img/closeUserData.svg";
import {useRef} from "react";
import {NavLink, useNavigate} from "react-router-dom";
import axios from 'axios';
import Cookies from 'js-cookie';


const ModelTuningPage = (props) => {
    const fileInputRef = useRef(null);
    const modelNameRef = useRef(null);
    const modelDescriptionRef = useRef(null);
    const model = JSON.parse(Cookies.get("model"));
    const navigate = useNavigate();
    const handleFileUpload = () => {
        if (fileInputRef.current) {
            fileInputRef.current.click();
        }
    };
    const handleFormSubmit = async () => {
        const file = fileInputRef.current.files[0];
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post(`http://178.20.40.246:8888/finetune_model?token=${encodeURI(model.token)}`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            console.log(response);

            navigate('/');
        } catch (error) {
            alert("Error");
        }
    }

    return <section className={styles.modelCreationPage}>
        <NavLink to="/"><div className={styles.goBackBtn}>
            <CloseUserData/>
        </div></NavLink>
        <div className={styles.content}>
            <h3>Name</h3>
            <div className={styles.modelNameBlock}>
                <input type="text" className={styles.modelNameInput} ref={modelNameRef} value={model.model_name} disabled={true}/>
                <div className={styles.modelTag}>Tag#{model.token}</div>

            </div>
            <div className={styles.loadJSON}>
                <h3>Load More Chat History</h3>
                <div>
                    <input type="file" ref={fileInputRef} style={{display: "none"}}/>
                    <input type="button" className={styles.json} onClick={handleFileUpload} value="JSON"/>
                </div>
            </div>
            <div className={styles.fineTuneBtn} onClick={handleFormSubmit} style={{marginBottom: "10px"}}>
                Fine-Tune Model
            </div>
            <a style={{
                textDecoration: "underline",
                marginLeft: "30px",
            }} href="https://www.makeuseof.com/how-to-export-telegram-chat-history/#:~:text=Navigate%20to%20Settings%20%3E%20Advanced.,to%20export%20your%20chat%20history">How to get history</a>

        </div>
    </section>
}

export {ModelTuningPage}