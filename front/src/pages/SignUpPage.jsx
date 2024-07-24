import styles from "./ModelCreationPage.module.css"
import pageStyles from "./SingUpPage.module.css"
import {ReactComponent as CloseUserData} from "../img/closeUserData.svg";
import {useRef} from "react";
import { NavLink } from "react-router-dom";
import axios from "axios";
import Cookies from 'js-cookie';
import { useNavigate } from 'react-router-dom';




const SignUpPage = (props) => {
    const emailRef = useRef(null);
    const usernameRef = useRef(null);
    const passwordRef = useRef(null);
    const navigate = useNavigate();

    const handleFormSubmission = async () => {
        axios.request({
            method: 'post',
            maxBodyLength: Infinity,
            url: 'http://178.20.40.246:8888/auth/register',
            headers: {
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({
                "email": emailRef.current.value,
                "username": usernameRef.current.value,
                "password": passwordRef.current.value,
                "is_active": true,
                "is_superuser": false,
                "is_verified": false,
                "status_id": 0,
            })
        }).then((response) => {
                Cookies.set('user_email', emailRef.current.value);
                Cookies.set('user_name', usernameRef.current.value);
                navigate('/');
                props.setIsUser(true);
            })
            .catch((error) => {
                alert("Error");
            });
    }

    return <section className={styles.modelCreationPage}>
        <NavLink to="/"><div className={styles.goBackBtn}>
            <CloseUserData/>
        </div></NavLink>
        <div className={pageStyles.content}>
            <div className={pageStyles.form}>
                <h2 className={pageStyles.title}>Sign Up</h2>
                <input type="text" ref={emailRef} placeholder={"Email"}/>
                <input type="text" ref={usernameRef} placeholder={"Username"}/>
                <input type="password" ref={passwordRef} placeholder={"Password"}/>
                <input type="button" value="Send" onClick={handleFormSubmission}/>
            </div>
        </div>
    </section>
}

export {SignUpPage}