import styles from "./ModelCreationPage.module.css"
import pageStyles from "./SingUpPage.module.css"
import {ReactComponent as CloseUserData} from "../img/closeUserData.svg";
import {useRef} from "react";
import { NavLink } from "react-router-dom";
import axios from "axios";
import Cookies from 'js-cookie';
import { useNavigate } from 'react-router-dom';
import qs from 'qs';




const LoginPage = (props) => {
    const emailRef = useRef(null);
    const usernameRef = useRef(null);
    const passwordRef = useRef(null);
    const navigate = useNavigate();

    const handleFormSubmission = async () => {
        let data = qs.stringify({
            'username': usernameRef.current.value,
            'password': passwordRef.current.value
        });

        let config = {
            method: 'post',
            maxBodyLength: Infinity,
            url: 'http://178.20.40.246:8888/auth/jwt/login',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: data
        };

        try {
            await axios(config);
            Cookies.set("user_email", Cookies.get("backup_email"));
            Cookies.set('user_name', usernameRef.current.value);
            navigate('/');
            props.setIsUser(true);

            let config2 = {
                method: 'get',
                maxBodyLength: Infinity,
                url: 'http://178.20.40.246:8888/get_user_models?email=' + encodeURI(Cookies.get("user_email")),
                headers: { }
            };

            axios.request(config2)
                .then((response) => {
                    props.setUserModels(response.data);
                })
                .catch((error) => {
                    console.log(error);
                });
        } catch (error) {
            alert("Invalid Credentials");
        }
    }

    return <section className={styles.modelCreationPage}>
        <NavLink to="/"><div className={styles.goBackBtn}>
            <CloseUserData/>
        </div></NavLink>
        <div className={pageStyles.content}>
            <div className={pageStyles.form}>
                <h2 className={pageStyles.title}>Sign Up</h2>
                <input type="text" ref={usernameRef} placeholder={"Username"}/>
                <input type="password" ref={passwordRef} placeholder={"Password"}/>
                <input type="button" value="Send" onClick={handleFormSubmission}/>
            </div>
        </div>
    </section>
}

export {LoginPage}