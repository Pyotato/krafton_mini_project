//아이디 정규표현식
var idReg = /^[a-z]+[a-z0-9]{4,11}$/g;
//a~z까지 영문자로 반드시 시작하며, 영문 숫자 조합으로 5 ~12자리
var pwdReg = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#%&?])[A-Za-z\d@$!%*#?&]{8,16}$/g;
let user_pwd_input = document.getElementById("#pwd_input");
let user_id_input = document.getElementById("#id_input");

//현재 사용자 위치 찾기 > 자세한 내용은 geolocation.api mozilla.docs 확인!
function geoFindMe() {
  const status = $("#status");
  // const mapLink = $("#map-link");
  let my_location = $("#current_location_input");

  // mapLink.href = "";
  // mapLink.textContent = "";

  function success(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;
    // console.log(`Latitude: ${latitude} °, Longitude: ${longitude} °`);
    $.ajax({
      type: "POST",
      contentType: "application/json",
      url: "/api/location/user",
      data: JSON.stringify({ curr_location: `${latitude},${longitude}` }),
      success: function (response) {
        // my_location.val(response);
        console.log("geoFindMe", response);
        localStorage.setItem("my_location", `${latitude},${longitude}`);
        // address_si address_dong
        // location_cat location_specific
        let si = "";
        response.address_si === undefined
          ? (si = "")
          : (si = response.address_si);
        let gu = "";
        response.address_gu === undefined
          ? (gu = "")
          : (gu = response.address_gu);
        let dong = "";
        response.address_dong === undefined
          ? (dong = "")
          : (dong = response.address_dong);

        let loc = `${si} ${gu} ${dong}`;
        if (loc) {
          try {
            document.getElementById("current_location_input").value = loc;
          } catch (e) {
            console.log(e);
          }
        }

        if (response["msg"] == "foreign user_agent") {
          alert("대한민국으로 위치를 설정해주세요.");
        }
      },
    });
  }

  function error() {
    status.textContent = "Unable to retrieve your location";
  }

  if (!navigator.geolocation) {
    status.textContent = "Geolocation is not supported by your browser";
  } else {
    status.textContent = "Locating…";
    navigator.geolocation.getCurrentPosition(success, error);
  }
}

function register_user() {
  let pwd_sign_up = $("#pwd_sign_up").val();
  let id_sign_up = $("#id_sign_up").val();
  console.log(pwd_sign_up);
  console.log(id_sign_up);

  if (!idReg.test(id_sign_up)) {
    alert(
      "아이디는 영문으로 시작하여, 영문숫자포함 5~12자로 정해주시길 바랍니다."
    );
    id_sign_up.focus();
    return;
  }
  if (!pwdReg.test(pwd_sign_up)) {
    alert(
      "비밀번호는 영문 대소문자,숫자,특수문자[!,@,#,%,&,?] 조합 8~15자리로 정해주시길 바랍니다."
    );
    pwd_sign_up.focus();
    return;
  }

  $.ajax({
    type: "POST",
    contentType: "application/json",
    url: "/api/register",
    data: JSON.stringify({ user_id: id_sign_up, pwd: pwd_sign_up }),
    success: function (response) {
      if (response["result"] == "success") {
        alert("회원가입을 축하드립니다!");
        window.location.replace("/login");
        console.log(response);
        return;
      }
      if (response["result"] == "fail") {
        alert("이미 있는 회원입니다.");
        user_id_input.focus();
        $("#pwd_sign_up:text").val("");
      }
    },
  });
}

function on_user_login() {
  $.ajax({
    type: "POST",
    contentType: "application/json",
    url: "/token",
    // url: "/api/login",
    data: JSON.stringify({
      user_id: user_id_input.value,
      pwd: user_pwd_input.value,
    }),
    success: function (response) {
      if (response["result"] == "success") {
        // alert("포스팅 성공!");
        // const userToken = localStorage.getItem("token");
        // localStorage.setItem("token", userToken);
        console.log("로그인 성공!", response);
        window.location = `/`;
        // city.val(response);
        // localStorage.setItem("token", userToken);
        // if()
      }
    },
  });
}

function logout() {
  $.ajax({
    type: "POST",
    contentType: "application/json",
    url: "/api/logout",

    success: function (response) {
      if (response["result"] == "success") {
        // alert("포스팅 성공!");
        // const userToken = localStorage.getItem("token");
        // localStorage.setItem("token", userToken);
        console.log("로그아웃 성공!", response);
        window.location = "/";
        // city.val(response);
        // localStorage.setItem("token", userToken);
        // if()
      }
    },
  });
}

// 주소 입력 -> 좌표 구하기 -> 컬렉션에 맞는 주소 찾기
function on_show_restaurant_list() {
  const input = document.getElementById("current_location_input").value;
  // localStorage.clear;
  geoFindMe();
  $.ajax({
    type: "POST",
    contentType: "application/json",
    url: "/api/location/user/find/me",
    data: JSON.stringify({ curr_location: input }),
    success: function (response) {
      console.log("response", response);

      // localStorage.setItem("my_location", response.my_coord);
      // geoFindMe();
      // window.location.replace("/restaurant/list");
      console.log("on_show_restaurant_list", JSON.stringify(response));
      location_city = response.my_location.address_si;
      window.location = `/restaurant/listcity/${response.my_location.address_si}`;
    },
  });
}
$(document).ready(geoFindMe());
