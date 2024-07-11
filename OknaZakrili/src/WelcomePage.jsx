import styles from "./WelcomePage.module.css";
import {ReactComponent as UserLogo} from "./img/userLogo.svg";
import {ReactComponent as Search} from "./img/search.svg";

const WelcomePage = (props) => {
    return <div className={styles.welcomePageBlock}>
        <div className={styles.topBlock}>
            <div className={styles.userData}>
                <p>Welcome Back,</p>
                <div className={styles.userBlock}>
                    <UserLogo />
                    <span>Emil</span>
                </div>
            </div>
            <div className={styles.searchBlock}>
                <Search />
                <input type="text" placeholder="Search For Models"/>
            </div>
        </div>
        <div className={styles.descriptionBlock}>
            <h1>Description</h1>
        </div>
    </div>
}

export {WelcomePage};