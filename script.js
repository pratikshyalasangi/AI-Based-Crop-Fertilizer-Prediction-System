
function togglePassword(id, icon) {
  const input = document.getElementById(id);
  if (!input) return;

  if (input.type === "password") {
    input.type = "text";
    icon.classList.replace("fa-eye", "fa-eye-slash");
  } else {
    input.type = "password";
    icon.classList.replace("fa-eye-slash", "fa-eye");
  }
}


function sendOTP() {
  const fullname = document.getElementById("name")?.value?.trim();
  const email = document.getElementById("email")?.value?.trim();
  const phone = document.getElementById("phone")?.value?.trim();
  const password = document.getElementById("password")?.value?.trim();

  if (!fullname || !email || !phone || !password) {
    alert("⚠️ Please fill all fields!");
    return;
  }

 
  const pending = { fullname, email, phone, password };
  sessionStorage.setItem("pending_registration", JSON.stringify(pending));


  const otp = String(Math.floor(100000 + Math.random() * 900000));
  sessionStorage.setItem("verify_otp", otp);
  sessionStorage.setItem("verify_email", email);


  alert(`🔐 Your OTP is: ${otp}`);


  window.location.href = "otp.html";
}


async function verifyOTP() {
  const enteredOTP = (document.getElementById("otpInput")?.value || "").trim();
  const savedOTP = sessionStorage.getItem("verify_otp");
  const pendingJSON = sessionStorage.getItem("pending_registration");

  if (!pendingJSON) {
    alert("⚠️ No pending registration found. Please register again.");
    window.location.href = "register.html";
    return;
  }

  if (!enteredOTP) {
    document.getElementById("otpMsg").innerText = "❌ Please enter OTP";
    return;
  }

  if (enteredOTP !== savedOTP) {
    document.getElementById("otpMsg").innerText = "❌ Incorrect OTP";
    return;
  }

 
  const pending = JSON.parse(pendingJSON);
  try {
    const resp = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(pending)
    });
    const data = await resp.json();

    if (data.status === "success") {
      
      sessionStorage.removeItem("pending_registration");
      sessionStorage.removeItem("verify_otp");

      alert("✅ Registration successful! Redirecting to Upload page...");
      
      window.location.href = "upload.html";
    } else {
      alert("❌ Registration failed: " + (data.message || data.msg || "Unknown error"));
    }
  } catch (err) {
    console.error("register error:", err);
    alert("❌ Registration error. Check console.");
  }
}

function resendOTP() {
  const pendingJSON = sessionStorage.getItem("pending_registration");
  if (!pendingJSON) {
    alert("⚠️ No pending registration found. Please register first.");
    window.location.href = "register.html";
    return;
  }

  const newOtp = String(Math.floor(100000 + Math.random() * 900000));
  sessionStorage.setItem("verify_otp", newOtp);
  alert(`🔄 OTP Resent! New OTP: ${newOtp}`);
}


async function loginUser() {
  const email = document.getElementById("loginEmail")?.value?.trim();
  const password = document.getElementById("loginPassword")?.value?.trim();

  if (!email || !password) {
    document.getElementById("loginMsg").innerText = "❌ Fill both fields";
    return;
  }

  const response = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  const data = await response.json();

  if (data.status === "success") {
    alert("✅ Login Successful!");
    window.location.href = "upload.html";
  } else {
    document.getElementById("loginMsg").innerText = "❌ Invalid email or password";
  }
}


let selectedFile = null;

function handleFileSelect(file) {
  if (!file) return;
  selectedFile = file;

  const reader = new FileReader();
  reader.onload = e => {
    const preview = document.getElementById("previewImage");
    if (preview) {
      preview.src = e.target.result;
      preview.style.display = "block";
    }
  };
  reader.readAsDataURL(file);
}

document.getElementById("cropImage")?.addEventListener("change", e => handleFileSelect(e.target.files[0]));
document.getElementById("cropImageGallery")?.addEventListener("change", e => handleFileSelect(e.target.files[0]));


async function predictCrop() {
  if (!selectedFile) {
    alert("⚠️ Please upload an image first!");
    return;
  }

  const formData = new FormData();
  formData.append("image", selectedFile);

  const response = await fetch("/upload", { method: "POST", body: formData });

  const html = await response.text();
  document.open();
  document.write(html);
  document.close();
}
