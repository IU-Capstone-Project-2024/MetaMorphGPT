import styles from './Navbar.module.css';
import {useState} from "react";
import {ReactComponent as CloseNavbar} from "./img/closeNavbar.svg";
import {ReactComponent as ModelLogo} from "./img/modelLogo.svg";
import {ReactComponent as PLusBtn} from "./img/plus.svg";
import {ReactComponent as CloseUserData} from "./img/closeUserData.svg";
import { NavLink } from "react-router-dom";


const Navbar = (props) => {
    const [isNavbarClosed, setIsNavbarClosed] = useState(false);
    const [isUser, setIsUser] = useState(false);
    return <div className={`${styles.navbarBlock} ${isNavbarClosed ? styles.navbarClosed : ""}`}>
        <div className={styles.topBlock}>
            <div className={styles.closeNavbar} setIsNavbarClosed={setIsNavbarClosed}>
                <CloseNavbar />
            </div>
            <NavLink to="/"><h3 className={styles.logo}>MetaMorphGPT</h3></NavLink>

            <div className={styles.modelsBlock}>
                <h3>Models</h3>
                <NavLink to="/create"><div className={styles.createBtn}>
                    <PLusBtn />
                    <span>Create</span>
                </div></NavLink>
                <div className={styles.model}>
                    <ModelLogo />
                    <span>Model1</span>
                </div>
                <div className={styles.model}>
                    <ModelLogo />
                    <span>Model2</span>
                </div>
                <div className={styles.model}>
                    <ModelLogo />
                    <span>Model3</span>
                </div>
            </div>
        </div>

        <div className={styles.downBlock}>
            {isUser ? <>
            <div className={styles.upgradeBtn}>
                <span>Upgrade</span>
            </div>
            <div className={styles.logOutBtn} onClick={() => {setIsUser(false)}}>
                <span>Log Out</span>
            </div>
            <div className={styles.userDataBlock}>
                <div className={styles.userData}>
                    <span className={styles.userDataName}>Emil</span>
                    <span className={styles.userDataAlias}>@emillogain</span>
                </div>
                <CloseUserData />
            </div>
            </>:
            <>
                <div className={`${styles.logOutBtn}`} onClick={() => {setIsUser(true)}}>
                    <span>Sign up</span>
                </div>
                <div className={`${styles.logOutBtn} ${styles.black}`} onClick={() => {setIsUser(true)}}>
                    <span>Log In</span>
                </div>
            </>}
        </div>
    </div>
}

export {Navbar};