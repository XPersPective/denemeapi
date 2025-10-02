from fastapi import APIRouter, Request, Response, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from core.database import get_db
from models.auth_models import UserCreate
from services.auth_service import AuthService
from fastapi import HTTPException

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home():
    """Ana sayfa"""
    return """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Crypto Trading API</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                padding: 50px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 600px;
                width: 100%;
                text-align: center;
            }
            h1 {
                color: #333;
                margin-bottom: 15px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #666;
                margin-bottom: 40px;
                font-size: 1.2em;
            }
            .btn-group {
                display: flex;
                gap: 20px;
                margin-top: 30px;
                justify-content: center;
            }
            .btn {
                padding: 18px 40px;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .btn-primary:hover {
                transform: translateY(-3px);
                box-shadow: 0 15px 30px rgba(102, 126, 234, 0.4);
            }
            .btn-secondary {
                background: #f0f0f0;
                color: #333;
            }
            .btn-secondary:hover {
                background: #e0e0e0;
                transform: translateY(-3px);
            }
            .features {
                margin-top: 50px;
                text-align: left;
            }
            .feature {
                margin: 20px 0;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 12px;
                border-left: 5px solid #667eea;
            }
            .feature-icon {
                font-size: 24px;
                margin-right: 10px;
            }
            .feature-title {
                font-weight: bold;
                color: #667eea;
                margin-bottom: 8px;
                font-size: 18px;
            }
            .api-links {
                margin-top: 30px;
                padding: 20px;
                background: #fff3cd;
                border-radius: 12px;
                border-left: 5px solid #ffc107;
            }
            .api-links a {
                color: #667eea;
                text-decoration: none;
                font-weight: bold;
                margin: 0 10px;
            }
            .api-links a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Crypto Trading API</h1>
            <p class="subtitle">Modern Cryptocurrency Tracking & Trading API</p>
            
            <div class="btn-group">
                <a href="/register" class="btn btn-primary">Kayıt Ol</a>
                <a href="/login" class="btn btn-secondary">Giriş Yap</a>
            </div>
            
            <div class="features">
                <div class="feature">
                    <span class="feature-icon">🔐</span>
                    <div class="feature-title">Güvenli Authentication</div>
                    <div>API key ve session token ile çift katmanlı güvenlik</div>
                </div>
                <div class="feature">
                    <span class="feature-icon">📊</span>
                    <div class="feature-title">Real-time Data</div>
                    <div>Anlık cryptocurrency verileri ve piyasa bilgileri</div>
                </div>
                <div class="feature">
                    <span class="feature-icon">⚡</span>
                    <div class="feature-title">Fast & Reliable</div>
                    <div>Yüksek performanslı ve güvenilir API servisleri</div>
                </div>
            </div>
            
            <div class="api-links">
                <strong>📚 API Dokümantasyonu:</strong><br><br>
                <a href="/auth/docs" target="_blank">Swagger UI</a>
                <a href="/auth/redoc" target="_blank">ReDoc</a>
            </div>
        </div>
    </body>
    </html>
    """


@router.get("/register", response_class=HTMLResponse)
async def register_form():
    """Kayıt formu"""
    return """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kayıt Ol - Crypto API</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 450px;
                width: 100%;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                text-align: center;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                text-align: center;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 500;
            }
            input {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.3s;
            }
            input:focus {
                outline: none;
                border-color: #667eea;
            }
            .btn {
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.2s;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
            }
            .links {
                text-align: center;
                margin-top: 20px;
                color: #666;
            }
            .links a {
                color: #667eea;
                text-decoration: none;
                font-weight: 500;
            }
            .links a:hover {
                text-decoration: underline;
            }
            .info {
                background: #e3f2fd;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 20px;
                border-left: 4px solid #2196f3;
                font-size: 14px;
                color: #1976d2;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Kayıt Ol</h1>
            <p class="subtitle">API erişimi için hesap oluşturun</p>
            
            <div class="info">
                ℹ️ Kayıt olduktan sonra otomatik olarak API anahtarınız oluşturulacaktır.
            </div>
            
            <form method="post" action="/register">
                <div class="form-group">
                    <label for="username">Kullanıcı Adı</label>
                    <input type="text" id="username" name="username" required minlength="3" maxlength="50"
                           placeholder="En az 3 karakter">
                </div>
                
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required 
                           placeholder="ornek@email.com">
                </div>
                
                <div class="form-group">
                    <label for="password">Şifre</label>
                    <input type="password" id="password" name="password" required minlength="8"
                           placeholder="En az 8 karakter">
                </div>
                
                <button type="submit" class="btn">Kayıt Ol</button>
            </form>
            
            <div class="links">
                Zaten hesabınız var mı? <a href="/login">Giriş Yap</a><br>
                <a href="/">← Ana Sayfaya Dön</a>
            </div>
        </div>
    </body>
    </html>
    """


@router.post("/register")
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Kullanıcı kayıt işlemi"""
    try:
        user_data = UserCreate(username=username, email=email, password=password)
        user = AuthService.create_user(db, user_data)
        
        # Başarılı kayıt - giriş sayfasına yönlendir
        return RedirectResponse(url="/login?success=registered", status_code=303)
    except HTTPException as e:
        # Hata durumunda formu tekrar göster
        error_message = e.detail
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Kayıt Ol - Crypto API</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    max-width: 450px;
                    width: 100%;
                }}
                h1 {{ color: #333; margin-bottom: 10px; text-align: center; }}
                .subtitle {{ color: #666; margin-bottom: 30px; text-align: center; }}
                .form-group {{ margin-bottom: 20px; }}
                label {{ display: block; margin-bottom: 8px; color: #333; font-weight: 500; }}
                input {{
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 14px;
                }}
                input:focus {{ outline: none; border-color: #667eea; }}
                .btn {{
                    width: 100%;
                    padding: 14px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                }}
                .error {{
                    background: #fee;
                    color: #c33;
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    border-left: 4px solid #c33;
                }}
                .links {{ text-align: center; margin-top: 20px; color: #666; }}
                .links a {{ color: #667eea; text-decoration: none; font-weight: 500; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Kayıt Ol</h1>
                <p class="subtitle">API erişimi için hesap oluşturun</p>
                
                <div class="error">⚠️ {error_message}</div>
                
                <form method="post" action="/register">
                    <div class="form-group">
                        <label for="username">Kullanıcı Adı</label>
                        <input type="text" id="username" name="username" value="{username}" required minlength="3" maxlength="50">
                    </div>
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" name="email" value="{email}" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Şifre</label>
                        <input type="password" id="password" name="password" required minlength="8">
                    </div>
                    <button type="submit" class="btn">Kayıt Ol</button>
                </form>
                
                <div class="links">
                    <a href="/login">Giriş Yap</a> | <a href="/">Ana Sayfa</a>
                </div>
            </div>
        </body>
        </html>
        """, status_code=400)
    except Exception as e:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html><body style="font-family: Arial; padding: 20px;">
            <h2>Hata</h2>
            <p>Beklenmeyen bir hata oluştu: {str(e)}</p>
            <a href="/register">Tekrar dene</a>
        </body></html>
        """, status_code=500)


@router.get("/login", response_class=HTMLResponse)
async def login_form(success: str = None, logout: str = None):
    """Giriş formu"""
    success_message = ""
    if success == "registered":
        success_message = """
        <div class="success">
            ✅ Kayıt başarılı! Şimdi giriş yapabilirsiniz.
        </div>
        """
    elif logout == "success":
        success_message = """
        <div class="success">
            ✅ Başarıyla çıkış yaptınız.
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Giriş Yap - Crypto API</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 450px;
                width: 100%;
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
                text-align: center;
            }}
            .subtitle {{
                color: #666;
                margin-bottom: 30px;
                text-align: center;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            label {{
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 500;
            }}
            input {{
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.3s;
            }}
            input:focus {{
                outline: none;
                border-color: #667eea;
            }}
            .btn {{
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.2s;
            }}
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
            }}
            .links {{
                text-align: center;
                margin-top: 20px;
                color: #666;
            }}
            .links a {{
                color: #667eea;
                text-decoration: none;
                font-weight: 500;
            }}
            .links a:hover {{
                text-decoration: underline;
            }}
            .success {{
                background: #d4edda;
                color: #155724;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 20px;
                border-left: 4px solid #28a745;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Giriş Yap</h1>
            <p class="subtitle">Hesabınıza giriş yapın</p>
            
            {success_message}
            
            <form method="post" action="/login">
                <div class="form-group">
                    <label for="username">Kullanıcı Adı</label>
                    <input type="text" id="username" name="username" required 
                           placeholder="Kullanıcı adınız">
                </div>
                
                <div class="form-group">
                    <label for="password">Şifre</label>
                    <input type="password" id="password" name="password" required
                           placeholder="Şifreniz">
                </div>
                
                <button type="submit" class="btn">Giriş Yap</button>
            </form>
            
            <div class="links">
                Hesabınız yok mu? <a href="/register">Kayıt Ol</a><br>
                <a href="/">← Ana Sayfaya Dön</a>
            </div>
        </div>
    </body>
    </html>
    """


@router.post("/login")
async def login_user(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Kullanıcı giriş işlemi"""
    from models.auth_models import UserLogin
    
    try:
        login_data = UserLogin(username=username, password=password)
        user = AuthService.authenticate_user(db, login_data)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Kullanıcı adı veya şifre hatalı"
            )
        
        # Session oluştur
        session = AuthService.create_session(db=db, user=user, expiry_hours=24)
        
        # Session token'ı cookie'ye kaydet
        redirect_response = RedirectResponse(url="/dashboard", status_code=303)
        redirect_response.set_cookie(
            key="session_token",
            value=session.session_token,
            httponly=True,
            max_age=86400,  # 24 saat
            samesite="lax"
        )
        
        return redirect_response
        
    except HTTPException as e:
        error_message = e.detail
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Giriş Yap - Crypto API</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    max-width: 450px;
                    width: 100%;
                }}
                h1 {{ color: #333; margin-bottom: 10px; text-align: center; }}
                .subtitle {{ color: #666; margin-bottom: 30px; text-align: center; }}
                .form-group {{ margin-bottom: 20px; }}
                label {{ display: block; margin-bottom: 8px; color: #333; font-weight: 500; }}
                input {{
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 14px;
                }}
                input:focus {{ outline: none; border-color: #667eea; }}
                .btn {{
                    width: 100%;
                    padding: 14px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                }}
                .error {{
                    background: #fee;
                    color: #c33;
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    border-left: 4px solid #c33;
                }}
                .links {{ text-align: center; margin-top: 20px; color: #666; }}
                .links a {{ color: #667eea; text-decoration: none; font-weight: 500; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔐 Giriş Yap</h1>
                <p class="subtitle">Hesabınıza giriş yapın</p>
                
                <div class="error">⚠️ {error_message}</div>
                
                <form method="post" action="/login">
                    <div class="form-group">
                        <label for="username">Kullanıcı Adı</label>
                        <input type="text" id="username" name="username" value="{username}" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Şifre</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn">Giriş Yap</button>
                </form>
                
                <div class="links">
                    <a href="/register">Kayıt Ol</a> | <a href="/">Ana Sayfa</a>
                </div>
            </div>
        </body>
        </html>
        """, status_code=401)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Kullanıcı dashboard - API anahtarı gösterimi"""
    # Cookie'den session token al
    session_token = request.cookies.get("session_token")
    
    if not session_token:
        return RedirectResponse(url="/login", status_code=303)
    
    # Session doğrula
    user, session = AuthService.verify_session(db, session_token)
    
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard - Crypto API</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 900px;
                margin: 0 auto;
            }}
            .header {{
                background: white;
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .header h1 {{
                color: #333;
                margin: 0;
            }}
            .logout-btn {{
                padding: 10px 20px;
                background: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
            }}
            .logout-btn:hover {{
                background: #d32f2f;
            }}
            .card {{
                background: white;
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 20px;
            }}
            .card-title {{
                color: #333;
                margin-bottom: 20px;
                font-size: 1.5em;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 10px;
                margin-bottom: 15px;
            }}
            .info-label {{
                font-weight: bold;
                color: #666;
            }}
            .info-value {{
                color: #333;
                font-family: 'Courier New', monospace;
            }}
            .api-key-container {{
                position: relative;
            }}
            .api-key {{
                background: #263238;
                color: #4caf50;
                padding: 15px;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                word-break: break-all;
                margin: 10px 0;
            }}
            .copy-btn {{
                padding: 10px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                margin-top: 10px;
            }}
            .copy-btn:hover {{
                background: #5568d3;
            }}
            .warning {{
                background: #fff3cd;
                color: #856404;
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid #ffc107;
                margin-top: 15px;
            }}
            .docs-section {{
                background: #e3f2fd;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #2196f3;
            }}
            .docs-section a {{
                color: #1976d2;
                text-decoration: none;
                font-weight: bold;
                margin: 0 10px;
            }}
            .docs-section a:hover {{
                text-decoration: underline;
            }}
            .badge {{
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }}
            .badge-success {{
                background: #d4edda;
                color: #155724;
            }}
        </style>
        <script>
            function copyApiKey() {{
                const apiKey = document.getElementById('api-key-text').textContent.trim();
                
                if (!navigator.clipboard) {{
                    alert('Tarayıcınız kopyalama özelliğini desteklemiyor.');
                    return;
                }}
                
                navigator.clipboard.writeText(apiKey).then(function() {{
                    const btn = document.getElementById('copy-btn');
                    btn.textContent = '✅ Kopyalandı!';
                    setTimeout(function() {{
                        btn.textContent = '📋 API Keyi Kopyala';
                    }}, 2000);
                }}).catch(function(err) {{
                    console.error('Hata:', err);
                    alert('Kopyalama başarısız');
                    const btn = document.getElementById('copy-btn');
                    btn.textContent = '❌ Hata';
                    setTimeout(function() {{
                        btn.textContent = '📋 API Keyi Kopyala';
                    }}, 2000);
                }});
            }}
            
            function logout() {{
                window.location.href = "/logout";
            }}
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <h1>👋 Hoş Geldin, {user.username}!</h1>
                    <span class="badge badge-success">Aktif</span>
                </div>
                <a href="/logout" class="logout-btn">Çıkış Yap</a>
            </div>
            
            <div class="card">
                <h2 class="card-title">👤 Kullanıcı Bilgileri</h2>
                <div class="info-row">
                    <span class="info-label">Kullanıcı ID:</span>
                    <span class="info-value">{user.id}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Kullanıcı Adı:</span>
                    <span class="info-value">{user.username}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Email:</span>
                    <span class="info-value">{user.email}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Kayıt Tarihi:</span>
                    <span class="info-value">{user.created_at.strftime('%d.%m.%Y %H:%M')}</span>
                </div>
            </div>
            
            <div class="card">
                <h2 class="card-title">🔑 API Anahtarı</h2>
                <p>API isteklerinizde bu anahtarı kullanın:</p>
                <div class="api-key-container">
                    <div class="api-key" id="api-key-text">{user.api_key}</div>
                    <button class="copy-btn" id="copy-btn" onclick="copyApiKey()">📋 API Keyi Kopyala</button>
                </div>
                <div class="warning">
                    <strong>⚠️ Önemli:</strong> API anahtarınızı kimseyle paylaşmayın ve güvenli bir yerde saklayın!
                </div>
            </div>
            
            <div class="card">
                <h2 class="card-title">📚 API Kullanımı</h2>
                <p><strong>API isteklerinizde header ekleyin:</strong></p>
                <div class="api-key">
                    X-API-Key: {user.api_key}<br>
                    # veya<br>
                    Authorization: Bearer {user.api_key}
                </div>
                
                <p style="margin-top: 20px;"><strong>Örnek kullanım (Python):</strong></p>
                <div class="api-key">
import requests<br><br>
headers = {{"X-API-Key": "{user.api_key}"}}<br>
response = requests.get("http://localhost:8000/symbols", headers=headers)<br>
print(response.json())
                </div>
                
                <div class="docs-section" style="margin-top: 20px;">
                    <strong>� API Dokümantasyonu:</strong><br><br>
                    <a href="/auth/docs" target="_blank" class="btn btn-outline-info">Swagger UI</a>
                    <a href="/auth/redoc" target="_blank" class="btn btn-outline-warning">ReDoc</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """


@router.get("/logout")
async def logout_get(request: Request, db: Session = Depends(get_db)):
    """Çıkış yap"""
    # Cookie'den session token al
    session_token = request.cookies.get("session_token")
    
    # Session'ı veritabanında geçersiz kıl
    if session_token:
        try:
            AuthService.invalidate_session(db, session_token)
        except:
            pass  # Session zaten geçersiz olabilir
    
    # Login sayfasına yönlendir ve cookie'yi sil
    response = RedirectResponse(url="/login?logout=success", status_code=303)
    response.delete_cookie(key="session_token", path="/", domain=None)
    response.set_cookie(
        key="session_token",
        value="",
        max_age=0,
        expires=0,
        path="/",
        httponly=True
    )
    return response
