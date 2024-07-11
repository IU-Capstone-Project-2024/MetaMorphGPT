import styles from "./ModelCreationPage.module.css"
import {ReactComponent as CloseUserData} from "./img/closeUserData.svg";
import {useRef} from "react";
import { NavLink } from "react-router-dom";

const ModelCreationPage = () => {
    const fileInputRef = useRef(null);
    const handleFileUpload = () => {
        if (fileInputRef.current) {
            fileInputRef.current.click();
        }
    };

    return <section className={styles.modelCreationPage}>
        <NavLink to="/"><div className={styles.goBackBtn}>
            <CloseUserData/>
        </div></NavLink>
        <div className={styles.content}>
            <div className={styles.modelNameBlock}>
                <h3 className={styles.modelName}>Model Vaino</h3>
                <div className={styles.modelTag}>Tag#xxxx</div>
            </div>
            <div className={styles.modelDescription}>
                <h3>Description</h3>
                <textarea
                    className={styles.textareaStyle}
                    rows={4}
                    placeholder="Hello, I’m Ivan Ivanov! I live in Russia and play balalaika."
                />
            </div>
            <div className={styles.loadJSON}>
                <h3>Load More Chat History</h3>
                <div>
                    <input type="file" ref={fileInputRef} style={{display: "none"}}/>
                    <input type="button" className={styles.json} onClick={handleFileUpload} value="JSON"/>
                </div>
            </div>
            <div className={styles.fineTuneBtn}>
                Fine-Tune Model
            </div>
        </div>
    </section>
}

export {ModelCreationPage}