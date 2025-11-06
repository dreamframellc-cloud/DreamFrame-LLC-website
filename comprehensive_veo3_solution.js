const express = require('express');
const { VertexAI } = require('@google-cloud/vertexai');
const { Storage } = require('@google-cloud/storage');
const cors = require('cors');
const axios = require('axios');
const { GoogleAuth } = require('google-auth-library');

const app = express();

// Middleware
app.use(cors({ origin: ['http://localhost:5000', 'https://dreamframellc.com'] }));
app.use(express.json());

// Initialize Google Cloud services
const projectId = 'dreamframe';
const storage = new Storage({
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
});

// Initialize Vertex AI
const vertexAI = new VertexAI({
  project: projectId,
  location: 'us-central1'
});

// Multiple endpoint variations to test for 404 fix (veo-3 is correct per Google docs)
const modelEndpoints = ['veo-3', 'veo-3.0-generate-001', 'video-generation'];

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'Comprehensive VEO 3 Server', endpoints: modelEndpoints });
});

// Get Google Cloud access token
async function getAccessToken() {
  try {
    const auth = new GoogleAuth({
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
      },
      scopes: ['https://www.googleapis.com/auth/cloud-platform']
    });
    
    const client = await auth.getClient();
    const token = await client.getAccessToken();
    return token.token;
  } catch (error) {
    console.error('Auth error:', error);
    throw error;
  }
}

// Check operation status with multiple endpoint attempts
async function checkOperationStatusComprehensive(operationId) {
  try {
    const accessToken = await getAccessToken();
    
    // Extract just the operation ID if full path provided
    const cleanOperationId = operationId.includes('/') ? operationId.split('/').pop() : operationId;
    
    // Try different endpoint variations to fix 404 errors
    for (const modelEndpoint of modelEndpoints) {
      try {
        const url = `https://us-central1-aiplatform.googleapis.com/v1/projects/${projectId}/locations/us-central1/publishers/google/models/${modelEndpoint}/operations/${cleanOperationId}`;
        
        const response = await axios.get(url, {
          headers: { Authorization: `Bearer ${accessToken}` },
          timeout: 10000
        });
        
        if (response.status === 200) {
          console.log(`✅ Status check successful with endpoint: ${modelEndpoint}`);
          return {
            success: true,
            data: response.data,
            endpoint: modelEndpoint
          };
        }
      } catch (error) {
        if (error.response?.status === 404) {
          console.log(`⚠️ 404 with endpoint: ${modelEndpoint}`);
          continue;
        } else {
          console.log(`❌ Error with endpoint ${modelEndpoint}:`, error.message);
        }
      }
    }
    
    // Try direct operations API as fallback
    try {
      const operationsUrl = `https://us-central1-aiplatform.googleapis.com/v1/projects/${projectId}/locations/us-central1/operations/${cleanOperationId}`;
      const response = await axios.get(operationsUrl, {
        headers: { Authorization: `Bearer ${accessToken}` },
        timeout: 10000
      });
      
      if (response.status === 200) {
        console.log('✅ Direct operations API successful');
        return {
          success: true,
          data: response.data,
          endpoint: 'operations-api'
        };
      }
    } catch (error) {
      console.log('❌ Direct operations API failed:', error.message);
    }
    
    return {
      success: false,
      error: 'All endpoint variations returned 404 - operation may not exist or VEO 3 API issue'
    };
    
  } catch (error) {
    return {
      success: false,
      error: `Status check failed: ${error.message}`
    };
  }
}

// Enhanced video generation with 404 fixes
app.post('/generate-video', async (req, res) => {
  try {
    const { prompt, aspectRatio = '16:9', durationSeconds = 5, resolution = '720p' } = req.body;
    console.log(`🎬 Comprehensive VEO 3: Received request: ${JSON.stringify(req.body)}`);

    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    // Try each model endpoint variation to fix 404 issues
    let operation, modelUsed;
    for (const modelEndpoint of modelEndpoints) {
      try {
        console.log(`🧪 Testing model endpoint: ${modelEndpoint}`);
        const model = vertexAI.getGenerativeModel({ model: modelEndpoint });
        
        const request = {
          contents: [{ role: 'user', parts: [{ text: prompt }] }],
          generationConfig: {
            aspectRatio,
            sampleCount: 1,
            durationSeconds: Number(durationSeconds),
            resolution
          }
        };

        operation = await model.generateContent(request, { timeout: 3600000 });
        modelUsed = modelEndpoint;
        console.log(`✅ Success with model: ${modelEndpoint}`);
        break;
        
      } catch (error) {
        console.log(`❌ Failed with model ${modelEndpoint}:`, error.message);
        if (modelEndpoint === modelEndpoints[modelEndpoints.length - 1]) {
          throw new Error('All model endpoint variations failed');
        }
      }
    }

    const operationId = operation.name.split('/').pop();
    console.log(`🔄 Operation ID: ${operationId} (using ${modelUsed})`);

    // Enhanced polling with comprehensive status checking
    const maxWaitSeconds = 14400; // 4 hours
    const startTime = Date.now();

    while (Date.now() - startTime < maxWaitSeconds * 1000) {
      try {
        const statusResult = await checkOperationStatusComprehensive(operationId);
        
        if (statusResult.success) {
          const status = statusResult.data;
          console.log(`📊 Status (${statusResult.endpoint}):`, JSON.stringify(status));

          if (status.done) {
            const response = status.response;
            if (response.raiMediaFilteredCount > 0) {
              console.warn(`Content filtered: raiMediaFilteredCount=${response.raiMediaFilteredCount}`);
              return res.status(400).json({ 
                error: 'Video generation failed due to content filtering',
                details: 'Prompt may violate safety policies'
              });
            }
            
            const videoUri = response.videos?.[0]?.gcsUri;
            if (!videoUri) {
              console.error('No video generated in response');
              return res.status(500).json({ error: 'No video generated' });
            }
            
            console.log(`🎥 Video completed: ${videoUri}`);
            return res.json({ 
              videoUri, 
              operationId, 
              status: 'success',
              endpoint: statusResult.endpoint,
              model: modelUsed
            });
          }
        } else {
          console.log(`⚠️ Status check failed: ${statusResult.error}`);
        }
      } catch (error) {
        console.error(`❌ Error during status check: ${error.message}`);
      }

      await new Promise(resolve => setTimeout(resolve, 30000)); // Poll every 30 seconds
    }

    console.error(`Operation ${operationId} timed out after ${maxWaitSeconds} seconds`);
    return res.status(504).json({ 
      error: `Operation ${operationId} timed out after ${maxWaitSeconds} seconds`,
      model: modelUsed
    });

  } catch (error) {
    console.error(`Error in /generate-video: ${error.message}`);
    if (error.code === 429) {
      return res.status(429).json({ 
        error: 'Quota exceeded, please try again later', 
        details: error.message 
      });
    }
    return res.status(500).json({ 
      error: 'Internal server error', 
      details: error.message 
    });
  }
});

// Test endpoint for checking specific operation status
app.get('/check-operation/:operationId', async (req, res) => {
  try {
    const { operationId } = req.params;
    console.log(`🔍 Checking operation: ${operationId}`);
    
    const result = await checkOperationStatusComprehensive(operationId);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(`Unhandled error: ${err.message}`);
  res.status(500).json({ error: 'Server error', details: err.message });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Comprehensive VEO 3 server running on port ${PORT}`);
  console.log(`📡 Endpoints available: ${modelEndpoints.join(', ')}`);
  console.log(`🔗 Health check: http://localhost:${PORT}/health`);
  console.log(`🔍 Operation check: http://localhost:${PORT}/check-operation/{id}`);
});