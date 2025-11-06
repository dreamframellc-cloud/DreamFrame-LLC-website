const express = require('express');
const { VertexAI } = require('@google-cloud/vertexai');
const cors = require('cors');
const app = express();

// Middleware
app.use(cors({ origin: ['http://localhost:5000', 'https://dreamframellc.com'] })); // Enable CORS for frontend requests
app.use(express.json()); // Parse JSON bodies

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'VEO 3 Node.js Server' });
});

// Initialize Vertex AI using your exact format
const vertexAI = new VertexAI({
  project: 'dreamframe',
  location: 'us-central1',
  googleAuthOptions: {
    credentials: {
      type: 'service_account',
      project_id: 'dreamframe',
      private_key_id: '5131dca848e6964f4d5239581bbd4d5a46cbabbf',
      private_key: `-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCKTwFYKTXJQHpz
nXH0oEgzet7BHRIV1QtlRMIRY3XK/ZyNuGuWbs8arnvo5mwYDIbdEbeRC947qsiq
vvoJDI/sthpr1fRwjuEwnm5rDffgvN3qpIFsj3KhNPlXBoOQ/i2rFm2E3bmuHMTR
K8yxq96/ifZ6Rf5zuKCBSJ/KgEflWuGls1tYddGTgQewiESegNJj+A5t3TaO418D
AhZ13WxH+NfW6UcCGILitCsbpSPjVOJTsrePKmo5l8TdZ+XJPrQbXMfbsBU8vOhs
KMw10Vfo9L/jakkNANbnfPNy6vprK27DzYezaoS6+IPalPaEMbu7UyP/Pr1R+CUE
O01GdsWdAgMBAAECggEAGe5Olvgg/rLBUpBcF2x+pPI+NdAsvh2jpZCy3v46DT0n
3zVKrJlpaHv6vNOIxCiDF4sVEtN6Ds9KEKM+Lzik+lE5GmsyiXDsXQhzNMyZYxAd
/jpqDo/Fgt5y+iM9Qw+4wbkyfuTwRWnc58exuMT7vgcQiGO7nXgp1ZtnZBjRgflV
wokYFZusE7TsQ66K3m+B1RF5yicgjAzDvAd/0ADWdRDRlOMIHpoXnndGqTl9fJEw
0S9+Q9b4r7ksdqpViC95qPzyIlKcWnRLmfAYKCfAjIA3+5UxN3b+B2JRaZhvTBVC
N0BisLpYt7ff950seBEEtmIf9FfRTKEUEuQm6Z0MYQKBgQC8p728hQyRLq14dRnF
6SszMWq8ZR8ZM4TLweQq+AyyhJ4+tE6xctN/WGHnPPFvuNv19gpr9+F8jszKWkED
cAhYAKzFvFkLEzopAf/t7mkaAtIM4d/lRTFqUHWUwZI0aYVrNPmTZ0bXzAYOvN3Z
SDbRUvv3646UeuKbLYINX9zB/QQKBgQC7rlZ9CHi2UKXpVvKfK0rK7tVJP+trqlDQ
MIBp38bJ0XQDadXCc0Ic+73uNVxAVwYB2qdCgV3921cmX1y8zdrPf1pZd0XGSW/J
fRLJbb/+LnURtr70VpCKTtG5mzqTcMNzwdw2EeU8P4Hjs4Cz8Q3P4ciatuvtA8Q4
0Z6h3WIUIQKBgQC1xEijYu4A1CB/dxQmA8qDwJE+g4+7EFBaoa3dWLGjLvPpJoDL
p/7vK5Do42ccZdhI246fCG5RPKVEMkGBtmfTopLU0exZJ2VaLXsRHCxXy2/myZqX
pFtAO9WORhNAPIs4CAqPY2p2cTVE7eQyfcmTVYlADc2Kcfvz15z+leZ1YQKBgG81
KVhjGavl87lk5NS9wU6n4EfMEUI1pDcIVj7l8xOJAbY4EwpqY0VrQaqRgb06E3wr
xKoan8gZHPXG0duqGrqS2sVicDzDLPL2IpiqaHZDrui1IUcEuBbMB2d0fGv7CEVi
HIsJZYyikOOMbHmzHx0Ly2Mpenhxn+aPBvEgjcohAoGBAKEMHXcfpej4fwuKIlCh
sMPRDbMnebwoEyJMzR8p/Ju2AXWtP6/3jh7G1dMFxmvSdq80jIJeoDR00QuRQzz+
lSepVFr4tzghcWjT9++kdOUcWn9DjQkoBjRmXw31qctpQeq6wZeM1OdI/YzDx18N
/rORf1vl65kWO6XEIlBKDWFO
-----END PRIVATE KEY-----`,
      client_email: 'dream-frame-robot@dreamframe.iam.gserviceaccount.com',
      client_id: '112701717089738923417',
      auth_uri: 'https://accounts.google.com/o/oauth2/auth',
      token_uri: 'https://oauth2.googleapis.com/token',
      auth_provider_x509_cert_url: 'https://www.googleapis.com/oauth2/v1/certs',
      client_x509_cert_url: 'https://www.googleapis.com/robot/v1/metadata/x509/dream-frame-robot%40dreamframe.iam.gserviceaccount.com',
      universe_domain: 'googleapis.com'
    }
  }
});

// Initialize Veo 3 model
const model = vertexAI.getGenerativeModel({ model: 'veo-3' });

// Endpoint for video generation (triggered by create_video_link.html)
app.post('/generate-video', async (req, res) => {
  try {
    const { prompt, aspectRatio = '16:9', durationSeconds = 5, resolution = '720p' } = req.body;
    console.log(`🎬 VEO 3 Node.js: Received request: ${JSON.stringify(req.body)}`);

    // Validate input
    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    // API request for Veo 3 video generation using your format
    const request = {
      contents: [{ role: 'user', parts: [{ text: prompt }] }],
      generationConfig: {
        aspectRatio,
        sampleCount: 1,
        durationSeconds,
        resolution
      }
    };

    console.log(`🚀 Sending request to Vertex AI VEO 3: ${JSON.stringify(request)}`);
    const operation = await model.generateContent(request, { timeout: 3600000 }); // 1-hour timeout

    const operationId = operation.name.split('/').pop();
    console.log(`✅ VEO 3 Operation ID: ${operationId}`);

    // Poll operation status with retry logic matching your approach
    const maxWaitSeconds = 14400; // 4 hours
    const startTime = Date.now();
    let status;

    while (Date.now() - startTime < maxWaitSeconds * 1000) {
      try {
        status = await retryOperation(operation, 5, 1000, 60000); // Retry up to 5 times, 1s to 60s delay
        console.log(`📊 Operation Status: ${JSON.stringify(status)}`);

        if (status.done) {
          const response = status.response;
          if (response.raiMediaFilteredCount > 0) {
            return res.status(400).json({ error: 'Video generation failed due to content filtering' });
          }
          const videoUri = response.videos?.[0]?.gcsUri;
          if (!videoUri) {
            console.error('No video generated in response');
            return res.status(500).json({ error: 'No video generated' });
          }
          console.log(`🎥 VEO 3 video completed: ${videoUri}`);
          return res.json({ videoUri, operationId, status: 'success' });
        }
      } catch (error) {
        if (error.code === 5) { // 404 Not Found
          console.error(`❌ Operation ${operationId} not found: ${error.message}`);
          return res.status(404).json({ error: `Operation ${operationId} not found`, details: error.message });
        }
        console.error(`⚠️ Error polling operation ${operationId}: ${error.message}`);
        return res.status(500).json({ error: 'Failed to poll operation', details: error.message });
      }
      await new Promise(resolve => setTimeout(resolve, 30000)); // Poll every 30 seconds
    }

    return res.status(504).json({ error: `Operation ${operationId} timed out after ${maxWaitSeconds} seconds` });
  } catch (error) {
    console.error(`❌ Error in /generate-video: ${error.message}`);
    if (error.code === 429) {
      return res.status(429).json({ error: 'Quota exceeded, please try again later', details: error.message });
    }
    return res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// Retry function for operation polling
async function retryOperation(operation, maxAttempts, minDelayMs, maxDelayMs) {
  let attempts = 0;
  while (attempts < maxAttempts) {
    try {
      return await operation.get();
    } catch (error) {
      if (error.code !== 5 || attempts === maxAttempts - 1) throw error; // Rethrow if not 404 or last attempt
      attempts++;
      const delayMs = Math.min(minDelayMs * Math.pow(2, attempts), maxDelayMs);
      console.log(`🔄 Retrying operation after ${delayMs}ms (attempt ${attempts})`);
      await new Promise(resolve => setTimeout(resolve, delayMs));
    }
  }
  throw new Error('Max retry attempts reached');
}

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(`Unhandled error: ${err.message}`);
  res.status(500).json({ error: 'Server error', details: err.message });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 VEO 3 Node.js server running on port ${PORT}`);
  console.log(`📡 Ready to handle video generation requests`);
  console.log(`🔗 Health check available at: http://localhost:${PORT}/health`);
});