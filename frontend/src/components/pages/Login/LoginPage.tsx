import { observer } from "mobx-react-lite";
import LogoBig from "./LogoBig.svg";
import { useState } from "react";
import { AuthService } from "@/stores/auth.service";
import { Navigate } from "@tanstack/react-router";

const ADMIN_EMAIL = "operator4@test.com";
const ADMIN_PASSWORD = "operator4";
const USER_EMAIL = "user0@test.com";
const USER_PASSWORD = "password0";

export const LoginPage = observer(() => {
  const [email, setEmail] = useState(ADMIN_EMAIL);
  const [password, setPassword] = useState(ADMIN_PASSWORD);
  const [disabled, setDisabled] = useState(false);
  const [error, setError] = useState(false);
  const [navigate, setNavigate] = useState(false);

  const onSubmit = async () => {
    setDisabled(true);

    const res = await AuthService.login(email, password);
    if (!res) {
      setError(true);
    }

    setNavigate(true);
    setDisabled(false);
  };

  return (
    <div
      className="flex flex-col h-full text-white"
      style={{
        background:
          "radial-gradient(164.29% 114.31% at 107.64% 107.47%, #487694 1.58%, #213342 72.38%, #182430 100%)"
      }}>
      {navigate && <Navigate to="/" />}
      <div className="flex items-center justify-between pt-10 w-full mx-auto px-6 md:px-28 h-fit">
        <LogoBig />
        <a href="https://cbr.ru/" className="font-light">
          Вернуться на сайт ⟶
        </a>
      </div>
      <div className="flex flex-1 justify-center items-center mx-auto">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
          }}
          className="flex flex-col w-[390px]">
          <h1 className="mb-8 text-center text-2xl font-medium">Войти на сайт</h1>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="border border-[#CCCFDD] rounded-xl px-4 py-5 bg-white/10 outline-none mb-3"
            placeholder="Почта"
            disabled={disabled}
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="border border-[#CCCFDD] rounded-xl px-4 py-5 bg-white/10 outline-none"
            placeholder="Пароль"
            disabled={disabled}
          />
          {error && <p className="text-red-500 text-center mt-3">Неверный логин или пароль</p>}
          <button
            className="bg-primary rounded-xl text-light text-white h-[60px] w-full mt-10 disabled:opacity-50"
            disabled={disabled}>
            Войти
          </button>
          <button
            className="mt-4"
            type="button"
            onClick={() => {
              if (email !== ADMIN_EMAIL) {
                setEmail(ADMIN_EMAIL);
                setPassword(ADMIN_PASSWORD);
              } else {
                setEmail(USER_EMAIL);
                setPassword(USER_PASSWORD);
              }
            }}>
            {email === ADMIN_EMAIL ? "Вставить пользователя" : "Вставить админа"}
          </button>
        </form>
      </div>
    </div>
  );
});
