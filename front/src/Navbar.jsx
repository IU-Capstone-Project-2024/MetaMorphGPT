import styles from './Navbar.module.css';
import {useEffect, useState} from "react";
import {ReactComponent as CloseNavbar} from "./img/closeNavbar.svg";
import {ReactComponent as ModelLogo} from "./img/modelLogo.svg";
import {ReactComponent as PLusBtn} from "./img/plus.svg";
import {ReactComponent as CloseUserData} from "./img/closeUserData.svg";
import Cookies from 'js-cookie';
import {NavLink, useNavigate} from "react-router-dom";
import axios from "axios";


const Navbar = (props) => {
    const isUser = props.isUser;
    const setIsUser = props.setIsUser;
    const [isNavbarClosed, setIsNavbarClosed] = useState(false);
    const navigate = useNavigate();
    const [userPremium, setUserPremium] = useState(false);

    useEffect(() => {
        let config = {
            method: 'get',
            maxBodyLength: Infinity,
            url: 'http://178.20.40.246:8888/check_premium?email=' + encodeURI(Cookies.get("user_email")),
            headers: { }
        };

        axios.request(config)
            .then((response) => {
                setUserPremium(response.data[0].is_premium);
            })
            .catch((error) => {
                console.log(error);
            });
    })

    const changeUserPremium = () => {
        setUserPremium(true);

        let config = {
            method: 'post',
            maxBodyLength: Infinity,
            url: 'http://178.20.40.246:8888/upgrade?email=' + encodeURI(Cookies.get("user_email")),
            headers: { }
        };

        axios.request(config)
            .then((response) => {
                console.log(JSON.stringify(response.data));
            })
            .catch((error) => {
                console.log(error);
            });
    }

    const logout = () => {
        Cookies.remove("user_name");
        Cookies.set("backup_email", Cookies.get("user_email"));
        Cookies.remove("user_email");
        setIsUser(false);

        props.setUserModels([]);
    }

    const handleModelOpening = (model) => {
        Cookies.set("model", model);
        navigate("/fine-tune")
    }
    return <div className={`${styles.navbarBlock} ${isNavbarClosed ? styles.navbarClosed : ""}`}>
        <div className={styles.topBlock}>
            <NavLink to="/"><h3 className={styles.logo}>MetaMorphGPT</h3></NavLink>

            <div className={styles.modelsBlock}>
                <h3>Models</h3>
                <NavLink to="/create"><div className={styles.createBtn}>
                    <PLusBtn />
                    <span>Create</span>
                </div></NavLink>
                {props.userModels && props.userModels.filter(model => {if(props.modelSearch === "") return true; else return model.model_name.includes(props.modelSearch)}).map((model) =>
                    <div className={styles.model} onClick={() => {handleModelOpening(JSON.stringify(model))}} key={model.token}>
                        <ModelLogo />
                        <span>{model.model_name}</span>
                    </div>
                )}
            </div>
        </div>

        <div className={styles.downBlock}>
            {isUser ? <>
            {!userPremium ?
            <div className={styles.upgradeBtn} onClick={changeUserPremium}>
                <span>Upgrade</span>
            </div> : null
            }
            <div className={styles.logOutBtn} onClick={logout}>
                <span>Log Out</span>
            </div>
            <div className={styles.userDataBlock}>
                <div className={styles.userData}>
                    <span className={styles.userDataName}>{Cookies.get("user_name")}</span>
                    <span className={styles.userDataAlias}>{Cookies.get("user_email")}</span>
                </div>
            </div>
            </>:
            <>
                <NavLink to="/signup">
                    <div className={`${styles.logOutBtn}`}>
                        <span>Sign up</span>
                    </div>
                </NavLink>
                <NavLink to="/login">
                    <div className={`${styles.logOutBtn} ${styles.black}`}>
                        <span>Log In</span>
                    </div>
                </NavLink>
            </>}
        </div>
    </div>
}

export {Navbar};