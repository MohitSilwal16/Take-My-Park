import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:webview_flutter/webview_flutter.dart';

void main() {
  runApp(
    MaterialApp(debugShowCheckedModeBanner: false, home: const MyWebViewPage()),
  );
}

class MyWebViewPage extends StatefulWidget {
  const MyWebViewPage({super.key});

  @override
  State<MyWebViewPage> createState() => _MyWebViewPageState();
}

class _MyWebViewPageState extends State<MyWebViewPage> {
  late final WebViewController _controller;

  @override
  void initState() {
    super.initState();

    // For Android, enable hybrid composition.
    // Required on Android for displaying WebView.
    // iOS does not require this.
    // This is optional if your Flutter version already supports it.
    // WebView.platform = SurfaceAndroidWebView();

    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onNavigationRequest: (NavigationRequest request) {
            final url = request.url;

            // Check if it's a Google Maps URL
            if (url.contains("google.com/maps") ||
                url.contains("goo.gl/maps")) {
              launchUrl(
                Uri.parse(url),
                mode: LaunchMode.externalNonBrowserApplication,
              );
              return NavigationDecision.prevent; // Stop WebView from loading
            }
            return NavigationDecision.navigate;
          },
        ),
      )
      ..loadRequest(Uri.parse('http://10.0.2.2:5000'));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(body: WebViewWidget(controller: _controller));
  }
}
