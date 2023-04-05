// console.log("hi!");

// $("#submit_form_btn").click(function (e) {
//   // alert("!!!!!");
//   e.preventDefault();
//   var id_value = $("#user_id_input").val();
//   var pwd_value = $("#user_pwd_input").val();
//   alert(`id_value : ${id_value},pwd_value : ${pwd_value} `);
// });

// $("#find-me").click(geoFindMe());

//아이디 정규표현식
var idReg = /^[a-z]+[a-z0-9]{4,11}$/g;
//a~z까지 영문자로 반드시 시작하며, 영문 숫자 조합으로 5 ~12자리
var pwdReg = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#%&?])[A-Za-z\d@$!%*#?&]{8,16}$/g;

//현재 사용자 위치 찾기 > 자세한 내용은 geolocation.api mozilla.docs 확인!
function geoFindMe() {
  const status = $("#status");
  const mapLink = $("#map-link");
  let my_location = $("#current_location_input");

  mapLink.href = "";
  mapLink.textContent = "";

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
        my_location.val(response);
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

$(document).ready(geoFindMe());

function submit_signup_form() {
  let user_pwd_input = $("#user_pwd_input").val();
  let user_id_input = $("#user_id_input").val();

  if (!idReg.test(user_id_input)) {
    alert(
      "아이디는 영문으로 시작하여, 영문숫자포함 5~12자로 정해주시길 바랍니다."
    );
    user_id_input.focus();
    return;
  }
  if (!pwdReg.test(user_pwd_input)) {
    alert(
      "비밀번호는 영문 대소문자,숫자,특수문자[!,@,#,%,&,?] 조합 8~15자리로 정해주시길 바랍니다."
    );
    user_pwd_input.focus();
    return;
  }

  $.ajax({
    type: "POST",
    contentType: "application/json",
    url: "/api/register",
    data: JSON.stringify({ user_id: user_id_input, pwd: user_pwd_input }),
    success: function (response) {
      if (response["result"] == "success") {
        alert("회원가입을 축하드립니다!");
        window.location.replace("/login");
        // window.location.reload();
        console.log(response);
        return;
        // localStorage.setItem("token", userToken);
      }
      if (response["result"] == "fail") {
        alert("이미 있는 회원입니다.");
        user_id_input.focus();
        $("#user_pwd_input:text").val("");
        // user_pwd_input.val("");
      }
    },
  });
}

function submit_login_form() {
  let user_pwd_input = $("#pwd_input").val();
  let user_id_input = $("#id_input").val();

  $.ajax({
    type: "POST",
    contentType: "application/json",
    url: "/api/login",
    data: JSON.stringify({ user_id: user_id_input, pwd: user_pwd_input }),
    success: function (response) {
      if (response["result"] == "success") {
        // alert("포스팅 성공!");
        const userToken = localStorage.getItem("token");
        localStorage.setItem("token", userToken);
        window.location.reload();
        console.log("로그인 성공!", response);
        // localStorage.setItem("token", userToken);
      } else if (response["result"] == "incorrect pwd") {
        alert("비밀번호가 불일치합니다.");
        user_id_input.val("");
      }
    },
  });
}
